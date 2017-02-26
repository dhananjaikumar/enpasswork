from django.http import HttpResponseRedirect
import re
from .models import UserProfile,TeamUser
from django.contrib.auth.models import Permission

class PasswordChangeMiddleware:
    def process_request(self, request):
        try:
            profile= UserProfile.objects.get(user=request.user)
            if profile.force_password_change and not request.user.is_superuser and request.user.is_staff and \
                    re.match(r'^/admin/?', request.path) and not re.match(r'^/admin/password_change/?', request.path) and not \
                    re.match(r'^/admin/logout/?',request.path):
                return HttpResponseRedirect('/admin/password_change/')
        except:
            pass