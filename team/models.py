from __future__ import unicode_literals
import os, random, string
from django.contrib.auth.models import User
from django.db import models
from django.db.models import F, FloatField, Sum
from organizations.base import (OrganizationBase, OrganizationUserBase,OrganizationOwnerBase)
from organizations.fields import SlugField, AutoCreatedField, AutoLastModifiedField

Not_Team_Owner = 'You have not registered a Team.'
        

class TimeStampedModel(models.Model):
    created = AutoCreatedField()
    modified = AutoLastModifiedField()

    class Meta:
        abstract = True

class Team(OrganizationBase,TimeStampedModel):
    organizationId=models.CharField(max_length=256,unique=True, verbose_name='Organization Id')
    slug = SlugField(max_length=200, blank=False, editable=True,
            populate_from='name', unique=True,
            help_text="The name in all lowercase, suitable for URL identification")
    class Meta:
        verbose_name = 'Organization'
        verbose_name_plural ='Organizations'
        
    def no_of_licences(self):
        number=Order.objects.filter(organization=self,status='paid').aggregate(Sum('no_of_licence'))['no_of_licence__sum']
        return number+20 if number!=None else 20
    
    def no_of_active_users(self):
        return TeamUser.objects.filter(organization=self,active=True).count()
    

class TeamGroup(models.Model):
    name=models.CharField(max_length=256, )
    team=models.ForeignKey(Team,verbose_name="Organization")

    class Meta:
        verbose_name = 'Group'
        verbose_name_plural ='Groups'
    def __unicode__(self):
        return u'%s'%self.name

class TeamUser(OrganizationUserBase,TimeStampedModel):
    active = models.BooleanField(default=False)
    group=models.ForeignKey(TeamGroup,on_delete=models.SET_NULL,blank = True,null=True)
    email=models.CharField(max_length=256,unique=True)
    membername=models.CharField(max_length=256,blank = True,verbose_name='Name')
    organization=models.ForeignKey(Team,blank = True,null=True)
    user=models.OneToOneField(User,blank=True,null=True)

        
    def __unicode__(self):
        return u'%s'%self.user
        

    class Meta:
        verbose_name = 'Member'
        verbose_name_plural ='Members'


# class TeamOwner(OrganizationOwnerBase,TimeStampedModel):
#     class Meta:
#         verbose_name = 'Owner'
#         verbose_name_plural ='Owners'
    


class ImportedUser(models.Model):
    email=models.CharField(primary_key=True,max_length=256,)
    name=models.CharField(max_length=256,blank = True,)


from orderinfo.models import Order
    
