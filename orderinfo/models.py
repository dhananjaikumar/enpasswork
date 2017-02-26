from __future__ import unicode_literals
from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from team.models import Team



class OrderRequest(models.Model):
    no_of_licence=models.IntegerField(verbose_name='Number of licence',validators=[MinValueValidator(1)])
    PAYMENT_CHOICES=(
    ('paypal','PayPal'),
    ('wire','Wire Transfer'),

    )
    preferred_payment_mathod = models.CharField(
    max_length=20,
    choices=PAYMENT_CHOICES,
    default='paypal',verbose_name="Preferred Payment Method"
    )
    message=models.TextField(blank = True)
    response=models.CharField(max_length=1000)
    organization=models.ForeignKey(Team,blank = True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    order_id = models.CharField(verbose_name='Order ID',unique=True,max_length=20)
    def __unicode__(self):
        return u'%s Licences'%self.no_of_licence

    class Meta:
        verbose_name = 'Purchase Order'
        verbose_name_plural ='Purchase Orders'


def file_validator(value):
    extension=value.name.split('/')[-1].split('.')[-1]

    if not extension=='pdf':
        raise ValidationError('The file must be a pdf type.')




class Order(models.Model):
    order_id = models.CharField(verbose_name='Order ID',max_length=20)
    no_of_licence=models.IntegerField(verbose_name='Number of licence',validators=[MinValueValidator(1)])
    price = models.FloatField(verbose_name='Net amount',default=0.0)
    currency=models.CharField(max_length=100)
    PAYMENT_CHOICES=(
    ('paypal','PayPal'),
    ('wire','Wire Transfer'),
    )
    payment_mathod = models.CharField(
    max_length=20,
    choices=PAYMENT_CHOICES,
    default='paypal',
    verbose_name="Payment Method"
    )
    organization=models.ForeignKey(Team)
    status=models.CharField(
    max_length=20,
    choices=(('quote','Quote'),('paid','Paid'),('cancel','Cancel'))
    )
    reason=models.TextField(verbose_name='Reason for cancellation',blank=True)
    invoice=models.FileField(upload_to='invoice',validators=[file_validator],blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return str(self.no_of_licence) + '('+str(self.organization)+')'
    
    class Meta:
        verbose_name = 'Order'
        verbose_name_plural ='Orders'
        



    
