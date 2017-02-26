import os
from django.contrib import admin
import random
from .models import Order,OrderRequest
from team.models import TeamUser
from django.contrib.auth.models import User
from common.util import EmailThread
from django_object_actions import DjangoObjectActions
from django.http.response import HttpResponseRedirect
# Register your models here.

def payment_mathod(method):
    if (method=='wire'):
        return 'Wire Transfer'
    if (method == 'paypal'):
        return 'PayPal'

class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_id','no_of_licence','created_at']
    def get_queryset(self, request):
        qs=super(OrderAdmin,self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        else:
            owner_org=TeamUser.objects.get(user=request.user).organization
            return qs.filter(organization=owner_org)

    def save_model(self, request, obj, form, change):
        try:
            user=User.objects.filter(teamuser__organization=obj.organization,is_staff=True)[0]
            admin=TeamUser.objects.filter(user=user,organization=obj.organization)[0]
            if (obj.status=='paid'):
                extra_context1 = {
                    'order_id': obj.order_id,
                    'licenses': obj.no_of_licence,
                }
                EmailThread(' Your Enpass order (%s) has been processed.'%obj.order_id, 'orderinfo/order_grant.html',[admin],extra_context=extra_context1).start()
            elif (obj.status=='cancel'):
                extra_context1 = {
                    'order_id': obj.order_id,
                    'licenses': obj.no_of_licence,
                    'method': payment_mathod(obj.payment_mathod),
                    'reason': obj.reason,
                    'time': OrderRequest.objects.get(order_id=obj.order_id).created_at
                }
                EmailThread('Cancellation of your Enpass order (%s).'%obj.order_id, 'orderinfo/order_cancel.html',[admin],extra_context=extra_context1).start()
            elif(obj.status=='quote'):
                extra_context1 = {
                    'order_id': obj.order_id,
                    'licenses': obj.no_of_licence,
                    'method': payment_mathod(obj.payment_mathod),
                    'time': OrderRequest.objects.get(order_id=obj.order_id).created_at,
                    'obj': obj
                }
                if 'invoice' in form.changed_data:
                    EmailThread('Quotation of your Enpass order ID %s.'%obj.order_id, 'orderinfo/order_quote.html',[admin],extra_context=extra_context1).start()
        except Exception as e:
            pass


        return super(OrderAdmin, self).save_model(request, obj, form, change)

    def get_actions(self, request):
        if request.user.is_superuser:
            return super(OrderAdmin, self).get_actions(request)
        else:
            return []

    def get_fieldsets(self, request, obj=None):
        fieldsets = super(OrderAdmin, self).get_fieldsets(request, obj)
        if obj and not request.user.is_superuser and not (obj.status=='cancel'):
            fieldsets=[(None, {
                'fields': ['no_of_licence', 'price', 'currency', 'payment_mathod', 'organization', 'status',
                           'invoice']})]

        return fieldsets

    def get_form(self, request, obj=None, **kwargs):
        form = super(OrderAdmin, self).get_form(request, obj, **kwargs)
        if not obj:
            try:
                order_req = OrderRequest.objects.get(order_id=request.GET.get('i', None))
                form.base_fields['order_id'].initial=order_req.order_id
                form.base_fields['no_of_licence'].initial =order_req.no_of_licence
                form.base_fields['payment_mathod'].initial =order_req.preferred_payment_mathod
                form.base_fields['organization'].initial = order_req.organization
            except:
                pass
        return form


    def change_view(self, request, object_id, form_url='', extra_context=None):
        if request.user.is_superuser:
            return super(OrderAdmin, self).change_view(request, object_id,form_url, extra_context=extra_context)
        else:
            extra_context = extra_context or {}
            extra_context['show_save_and_continue'] = False
            extra_context['show_save'] = False
            extra_context['show_delete'] = False
            return super(OrderAdmin, self).change_view(request, object_id,form_url, extra_context=extra_context)

    def has_add_permission(self, request):
        if request.user.is_superuser:
            return True
        else:
            return False

    def has_module_permission(self, request):
        if not request.user.is_authenticated():
            return False
        elif request.user.is_superuser:
            return True
        elif TeamUser.objects.filter(user=request.user).exists():
            return True
        else:
            return False
    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return super(OrderAdmin,self).get_readonly_fields( request, obj=None)
        if obj:
            return self.readonly_fields + ('no_of_licence','price','currency','payment_mathod','organization','status','reason','invoice')
        else:
            return []


class OrderRequestAdmin(DjangoObjectActions,admin.ModelAdmin):
    list_display = ['order_id','no_of_licence','created_at']
    search_fields = ['order_id','organization__name']

    def create_order(self, request, obj):
        return HttpResponseRedirect('/admin/orderinfo/order/add/?i=%s'%obj.order_id)

    create_order.label='Create Order'
    change_actions = ['create_order',]
    def has_module_permission(self, request):
        if not request.user.is_authenticated():
            return False
        elif request.user.is_superuser:
            return True
        elif TeamUser.objects.filter(user=request.user).exists():
            return True
        else:
            return False

    # def has_change_permission(self, request,obj=None):
    #     if request.user.is_superuser:
    #         return True
    #     else:
    #         return False

    def get_queryset(self, request):
        qs=super(OrderRequestAdmin,self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        else:
            owner_org=TeamUser.objects.get(user=request.user).organization
            return qs.filter(organization=owner_org)
    
    def save_model(self, request, obj, form, change):
        if not change:
            try:
                teamAdmin=TeamUser.objects.get(user=request.user)
                obj.organization=teamAdmin.organization
                obj.order_id=''.join(random.choice('0123456789') for i in range(15))
                obj.save()

                extra_context1 = {
                    'order_id': obj.order_id,
                    'licenses':obj.no_of_licence,
                    'method':payment_mathod(obj.preferred_payment_mathod),
                    'message':obj.message
                }

                EmailThread('Confirmation of your Enpass order (%s).' % obj.order_id,
                            'orderinfo/order_placement_confirmation.html', [teamAdmin],
                            extra_context=extra_context1).start()

                ''' An order confirmation mail to Sinew Software System '''
                superAdmin=TeamUser()
                # superAdmin.email='partner-support@enpass.io'
                superAdmin.email = 'dhananjai.kumar@sinew.in'
                superAdmin.membername=teamAdmin.email if not teamAdmin.membername else teamAdmin.membername
                superAdmin.organization = teamAdmin.organization

                EmailThread('New order request for Enpass Partner: Order ID %s '%obj.order_id , 'orderinfo/order_request.html',[superAdmin],extra_context=extra_context1).start()


            except:
                pass
        return super(OrderRequestAdmin,self).save_model(request,obj,form,change)
        
    def change_view(self, request, object_id, form_url='', extra_context=None):
        if request.user.is_superuser:
            self.change_actions = ['create_order',]
            return super(OrderRequestAdmin, self).change_view(request, object_id,form_url, extra_context=extra_context)
        else:
            self.change_actions = []
            extra_context = extra_context or {}
            extra_context['show_save_and_continue'] = False
            extra_context['show_save'] = False
            extra_context['show_delete'] = False
            return super(OrderRequestAdmin, self).change_view(request, object_id,form_url, extra_context=extra_context)

    def add_view(self, request,form_url='', extra_context=None):
        if request.user.is_superuser:
            return super(OrderRequestAdmin, self).add_view(request,form_url, extra_context=extra_context)
        else:
            extra_context = extra_context or {}
            extra_context['show_save_and_continue'] = False
            # extra_context['show_save_and_add_another'] = False
            # extra_context['save_and_add_another'] = 'Send and add another'
#            extra_context['show_save'] = False
#            extra_context['show_delete'] = False
            return super(OrderRequestAdmin, self).add_view(request, form_url, extra_context=extra_context)
    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return self.readonly_fields
        if obj:
            return self.readonly_fields + ('message','response','order_id','preferred_payment_mathod', 'no_of_licence',)
        else:
            return self.readonly_fields + ('response',)

    def get_fieldsets(self, request, obj=None):
        fieldsets = super(OrderRequestAdmin, self).get_fieldsets(request, obj)
        if request.user.is_superuser:
            fieldsets=[(
                None, {'fields': ['order_id','preferred_payment_mathod', 'organization', 'no_of_licence', 'message', 'response']}
            )]
        else:
            if obj:
                if not obj.response:
                    fieldsets=[(None, {'fields': ['order_id','preferred_payment_mathod', 'no_of_licence', 'message']})]
                else:
                    fieldsets = [(None, {
                        'fields': ['order_id', 'preferred_payment_mathod', 'no_of_licence', 'message', 'response']})]
            else:
                fieldsets = [(None, {
                    'fields': [ 'preferred_payment_mathod', 'no_of_licence', 'message', ]})]
        return fieldsets


admin.site.register(Order,OrderAdmin)
admin.site.register(OrderRequest,OrderRequestAdmin)

