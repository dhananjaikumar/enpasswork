from __future__ import unicode_literals

from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save,pre_save
from django.conf import settings
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from team.models import TeamUser


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)



class Otp(models.Model):
    teamuser= models.ForeignKey(TeamUser,on_delete=models.SET_NULL,null=True)
    one_time_password= models.CharField(max_length=6,)
    created_at = models.DateTimeField(auto_now_add=True)
    expired = models.BooleanField(default=False)
    def __str__(self):
        return self.one_time_password


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_UserProfile(sender, instance=None, created=False, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(pre_save, sender=settings.AUTH_USER_MODEL)
def password_changed_pre(sender, instance=None, created=False, **kwargs):
    try:
        user = User.objects.get(username=instance.username)
        if not user.password == instance.password:
            profile = UserProfile.objects.get(user=user)
            profile.force_password_change = False
            profile.save()
    except User.DoesNotExist:
        pass



class UserProfile(models.Model):
    user = models.OneToOneField(User)
    force_password_change = models.BooleanField(default=True)
    def __str__(self):
        return self.user.username