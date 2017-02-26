from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt
from .views import Signin1,Signin2,ResendOTP,TokenValidation

urlpatterns = [
    url(r'^signin1/$',Signin1.as_view()),
    url(r'^signin2/$',Signin2.as_view()),
    url(r'^resend_otp/$',ResendOTP.as_view()),
    url(r'^validate/$',TokenValidation.as_view())
]
