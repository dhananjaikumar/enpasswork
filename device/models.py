from __future__ import unicode_literals

from django.db import models
from team.models import TeamUser

class Device(models.Model):
    user=models.ForeignKey(TeamUser)
    device_id = models.CharField('Device Id',max_length=256)
    device_name = models.CharField('Device Name',max_length=256,blank=True)
    last_verified=models.DateTimeField('Last verified',auto_now=True)
    creation_date = models.DateTimeField("Creation date", auto_now_add=True)

    def __str__(self):
        return '%s(%s)'%(self.user.user.username,self.device_name)

