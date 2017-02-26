import os
import string
import random
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.admin import SimpleListFilter

from django.contrib import messages 
from import_export import resources
from import_export.formats import base_formats
from import_export.admin import ImportMixin
from .models import (Team,TeamUser,TeamGroup,ImportedUser)
from rest_framework.authtoken.models import Token
from common.util import EmailThread


def randomPassword():
    length = 20
    chars = string.ascii_letters+string.digits+string.punctuation
    random.seed = (os.urandom(1024))
    return ''.join(random.choice(chars) for i in range(length))


class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    prepopulated_fields = {"slug": ("name",)}
    def get_model_perms(self, request):
        if request.user.is_superuser:
            return super(TeamAdmin,self).get_model_perms(request)
        else:
            return {}



class GroupFilter(SimpleListFilter):
    title = 'Group'
    parameter_name = 'group'

    def lookups(self, request, model_admin):
        try:
            teamuser=TeamUser.objects.get(user=request.user)
            groups = TeamGroup.objects.filter(team=teamuser.organization)
            return [(group.id,group.name) for group in groups]
        except TeamUser.DoesNotExist:
            return TeamUser.objects.none()


    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(group=self.value())
        else:
            return queryset 

class ActiveFilter(SimpleListFilter):
    title='Active'
    parameter_name='active'
    def lookups(self,request,model_admin):
        return (
        (None,''),
        (2,'All'),
        (1,'Yes'),
        (0,'No'),
        )
    def choices(self, cl):
        for lookup, title in self.lookup_choices:
            yield {
                'selected': self.value() == lookup,
                'query_string': cl.get_query_string({
                    self.parameter_name: lookup,
                }, []),
                'display': title,
            }
    
    def queryset(self, request, queryset):
        if self.value() is None:
            self.used_parameters[self.parameter_name] = 1
        else:
            self.used_parameters[self.parameter_name] = int(self.value())
        if self.value()==2:
            return queryset
        return queryset.filter(active=self.value())

class UserResource(resources.ModelResource):

    organization=None

    def save_instance(self, instance, using_transactions=True, dry_run=False):
        if dry_run:
            instance.save()
        else:
            if self.organization==None:
                return
            try:
                user=User.objects.get(username=instance.email)
            except User.DoesNotExist:
                user=User.objects.create_user(instance.email,instance.email,randomPassword)
            try:
                obje, created=TeamUser.objects.update_or_create(
                user=user,
                email=instance.email,
                organization=self.organization,
                defaults={'active': False,'name':instance.name},
                )
            except:
                pass

    def before_import(self, dataset, using_transactions, dry_run, **kwargs):

        emails = dataset['email']
        teamusers=[user.email for user in TeamUser.objects.all()]
        for email in emails:
            if email in teamusers:
                del dataset[dataset['email'].index(email)]


        try:
            self.organization= TeamUser.objects.get(user=kwargs['user']).organization
        except:
            pass


    class Meta:
        model=ImportedUser
        report_skipped = True
        skip_unchanged = True
        import_id_fields = ('email',)
        fields =('email','name')

def deleteToken(teamuser):
    try:
        Token.objects.get(user=teamuser.user).delete()
    except:
        pass
        
        
class TeamUserAdmin(ImportMixin,admin.ModelAdmin):
    search_fields = ['user__email','user__username','membername']

    formats = (base_formats.CSV,)
    resource_class = UserResource
    list_display=('user','group','active')
    list_filter=(GroupFilter,'active')
    actions=('make_active','make_deactive')

    def has_module_permission(self, request):
        if not request.user.is_authenticated():
            return False
        elif request.user.is_superuser:
            return True
        elif TeamUser.objects.filter(user=request.user).exists():
            return True
        else:
            return False

    # def changelist_view(self,request, extra_context=None):
    #     if not request.user.is_superuser:
    #         owner_org = TeamUser.objects.get(user=request.user).organization
    #     if request.GET.get('q'):
    #         extra_context=extra_context or {}
    #         extra_context['insufficient_licence']="You do not have sufficient licenses."
    #     return super(TeamUserAdmin,self).changelist_view(request,extra_context=extra_context)


    def make_active(self,request, queryset):
        owner_org=TeamUser.objects.get(user=request.user).organization
        activated_users=[]

        if ((owner_org.no_of_active_users()+queryset.filter(active=False).count())>owner_org.no_of_licences()):
            messages.error(request, "You do not have sufficient licenses.")
        else:
            for a in queryset.filter(active=False):
                a.active=True
                a.save()
                activated_users.append(a)
        EmailThread('Enpass account activation for %s'%owner_org.name,'team/team_granted.html',activated_users).start()

        
    
    make_active.short_description='Activate Selected Members'
    
    def make_deactive(self,request,queryset):
        owner_org = TeamUser.objects.get(user=request.user).organization
        deactivated_users = queryset.filter(active=True)
        for a in deactivated_users:
            a.active=False
            a.save()
            deleteToken(a)
        EmailThread('Enpass account deactivation for %s' % owner_org.name, 'team/team_deactivation.html', deactivated_users).start()
    make_deactive.short_description='Deactivate Selected Members'
    
    def save_model(self, request, obj, form, change):
        if change:
            if request.user.is_superuser:
                return super(TeamUserAdmin, self).save_model(request, obj, form, change)

            owner_org = TeamUser.objects.get(user=request.user).organization

            '''check active field value change'''
            if 'active' in form.changed_data:
                if obj.active:
                    EmailThread('Your %s organization'%owner_org.name,'team/team_granted.html',[obj]).start()
                else:
                    deleteToken(obj)
                    EmailThread('Enpass account deactivation for %s' % owner_org.name, 'team/team_deactivation.html',
                                [obj]).start()

            return super(TeamUserAdmin, self).save_model(request, obj, form, change)
        else:
            if request.user.is_superuser:
                obj.email=obj.user.email
                obj.save()
            else:
                try:
                    user=User.objects.get(email=obj.email)
                    obj.user= user
                except User.DoesNotExist:
                    user=User.objects.create_user(obj.email,obj.email,randomPassword)
                owner_org=TeamUser.objects.get(user=request.user).organization
                obj.user=user
                obj.organization=owner_org
                obj.save()

            if obj.active:
                EmailThread('Enpass account activation for %s'%owner_org.name,'team/team_granted.html',[obj]).start()
            return super(TeamUserAdmin, self).save_model(request, obj, form, change)

    
    def get_queryset(self, request):
        qs=super(TeamUserAdmin,self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        else:
            try:
                owner_org=TeamUser.objects.get(user=request.user).organization
            except (TeamUser.DoesNotExist):
                return TeamUser.objects.none()
            return qs.filter(organization=owner_org)

    def get_fieldsets(self, request, obj=None):
        fieldsets = super(TeamUserAdmin, self).get_fieldsets(request, obj)
        if request.user.is_superuser:
            fieldsets=[(None, {'fields': ['membername','user', 'organization',]})]
        else:
            fieldsets=[(None, {'fields': ['membername', 'email','group','active',]})]

        return fieldsets

    def get_form(self, request, obj=None, **kwargs):
        form = super(TeamUserAdmin, self).get_form(request, obj, **kwargs)
        if request.user.is_superuser:
            form.base_fields['user'].required = True
        return form

    def change_view(self, request, object_id, form_url='', extra_context=None):
        if request.user.is_superuser:
            pass
        else:
            owner_org=TeamUser.objects.get(user=request.user).organization
            if owner_org.no_of_active_users() >= owner_org.no_of_licences() and not TeamUser.objects.get(id=object_id).active:
                messages.error(request,"You do not have sufficient licence for active member.")
        return super(TeamUserAdmin, self).change_view(request, object_id,form_url, extra_context=extra_context)
    
    def add_view(self, request,form_url='', extra_context=None):
        if request.user.is_superuser:
            pass
        else:
            owner_org=TeamUser.objects.get(user=request.user).organization
            if owner_org.no_of_active_users() >= owner_org.no_of_licences():
                messages.error(request,"You do not have sufficient licenses.")
        return super(TeamUserAdmin, self).add_view(request,form_url, extra_context=extra_context)
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "group":
            try:
                teamuser=TeamUser.objects.filter(user=request.user)[0]
                kwargs["queryset"] = TeamGroup.objects.filter(team=teamuser.organization)
            except:
                pass
        if request.user.is_superuser and db_field.name == "user":
            kwargs["queryset"] = User.objects.filter(is_staff=True, is_active=True).exclude(is_superuser=True)
        return super(TeamUserAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
    
    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return super(TeamUserAdmin,self).get_readonly_fields( request, obj=None)
        
        owner_org=TeamUser.objects.get(user=request.user).organization
        if owner_org.no_of_active_users() >= owner_org.no_of_licences():
            if obj:
                return self.readonly_fields + ('email',) if obj.active else self.readonly_fields + ('active','email',)
            else:
                return self.readonly_fields + ('active',)
        else:
            if obj:
                return self.readonly_fields + ('email',)
            else:
                return []



# class TeamOwnerAdmin(admin.ModelAdmin):
#     def get_model_perms(self, request):
#             return {}
#
#     def get_queryset(self, request):
#         qs=super(TeamOwnerAdmin,self).get_queryset(request)
#         if request.user.is_superuser:
#             return qs
#         else:
#             try:
#                 teamuser=TeamUser.objects.get(user=request.user)
#             except (TeamOwner.DoesNotExist,TeamUser.DoesNotExist):
#                 return []
#             return qs.filter(organization_user=teamuser)
#
#     def formfield_for_foreignkey(self, db_field, request, **kwargs):
#         if request.user.is_superuser:
#             return super(TeamOwnerAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
#
#         if db_field.name == "organization":
#             try:
#                 org=TeamUser.objects.get(user=request.user).organization
#                 kwargs['initial'] =org
#                 kwargs["queryset"] =Team.objects.filter(id=org.id)
#             except (Team.DoesNotExist,TeamUser.DoesNotExist):
#                 pass
#         if db_field.name=='organization_user':
#             kwargs["queryset"] =TeamUser.objects.filter(organization=TeamUser.objects.get(user=request.user).organization)
#         return super(TeamOwnerAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


class TeamGroupAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        if not request.user.is_authenticated():
            return False
        elif request.user.is_superuser:
            return True
        elif TeamUser.objects.filter(user=request.user).exists():
            return True
        else:
            return False

    def get_queryset(self, request):
        qs=super(TeamGroupAdmin,self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        else:
            try:
                teamuser=TeamUser.objects.get(user=request.user)
            except (TeamUser.DoesNotExist):
                return TeamUser.objects.none()
            return qs.filter(team=teamuser.organization )
    
    def save_model(self, request, obj, form, change):
        if request.user.is_superuser:
            return super(TeamGroupAdmin,self).save_model(request,obj,form,change)
        else:
            try:
                obj.team=TeamUser.objects.get(user=request.user).organization
                obj.save()
            except:
                pass
            return super(TeamGroupAdmin,self).save_model(request,obj,form,change)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        if TeamUser.objects.filter(user=request.user).exists():
            self.exclude=('team',)
        else:
            self.exclude = ()
        return super(TeamGroupAdmin,self).change_view(request,object_id=object_id,form_url=form_url,extra_context=extra_context)
    def add_view(self, request, form_url='', extra_context=None):
        if TeamUser.objects.filter(user=request.user).exists():
            self.exclude=('team',)
        else:
            self.exclude = ()
        return super(TeamGroupAdmin,self).add_view( request, form_url, extra_context)









admin.site.register(Team,TeamAdmin)
# admin.site.register(TeamOwner,TeamOwnerAdmin)
admin.site.register(TeamUser,TeamUserAdmin)
admin.site.register(TeamGroup,TeamGroupAdmin)

