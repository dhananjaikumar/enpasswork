from django.contrib import admin
from .models import TeamUser,Team

def activeMembers(request):
    try:
        organization=TeamUser.objects.get(user=request.user).organization
        admin.site.site_header = '%s'%organization
        return {
        'activeMembers':"%s / %s"%(organization.no_of_active_users(),organization.no_of_licences()),
        'organization_name':"%s"%(organization),
        }
    except: 
        return {'activeMembers':'0/0'}

