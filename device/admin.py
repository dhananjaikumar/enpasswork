from django.contrib import admin
from .models import Device
from  team.models import TeamUser
from django.contrib.admin import SimpleListFilter

class UserFilter(SimpleListFilter):
    title = 'User'
    parameter_name = 'user'

    def lookups(self, request, model_admin):
        try:
            owner_org = TeamUser.objects.get(user=request.user).organization
            teamusers = TeamUser.objects.filter(organization=owner_org)
        except:
            teamusers = TeamUser.objects.all()
        return [(teamuser.id, teamuser.email) for teamuser in teamusers]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(user=self.value())
        else:
            return queryset

class DeviceAdmin(admin.ModelAdmin):
    list_filter = [UserFilter]
    list_display = ['user','device_id']
    search_fields = ['user__email']
    def get_queryset(self, request):
        qs=super(DeviceAdmin,self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        else:
            try:
                owner_org = TeamUser.objects.get(user=request.user).organization
                return qs.filter(user__organization=owner_org)
            except TeamUser.DoesNotExist():
                return TeamUser.objects.none()
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            try:
                owner_org = TeamUser.objects.get(user=request.user).organization
                kwargs["queryset"] = TeamUser.objects.filter(organization=owner_org)
            except:
                pass
        return super(DeviceAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(Device,DeviceAdmin)