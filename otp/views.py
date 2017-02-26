import random
from rest_framework.views import *

from rest_framework.authtoken.models import Token

from rest_framework.throttling import AnonRateThrottle,UserRateThrottle
from rest_framework.authentication import BasicAuthentication
from team.models import Team,TeamUser
from common.util import EmailThread
from .models import Otp
from device.models import Device




'''
query: /api/signin1/
Method: POST
data: {
"organization_id": "oriental",
"email": "abi@gmail.com"
}
'''

class Signin1(APIView):
    authentication_classes = ( BasicAuthentication,)
    throttle_classes = (AnonRateThrottle,UserRateThrottle)
    def validate_device(self,user):
        # TODO: Uncommnet if require restriction
        # return (Device.objects.filter(user=user).count()<10)
        return True
    def post(self,request,format=None):
        organization_id=request.data['organization_id']
        email=request.data['email']
        if not organization_id or not email:
            return Response({'error':True,'description':'Organization Id and Email are required.'})
        try:
            team=Team.objects.get(organizationId=organization_id)
            teamuser=TeamUser.objects.get(email=email,organization=team)

        except Team.DoesNotExist:
            return Response({'error':True,'description':'Invalid organization ID.'})
        except TeamUser.DoesNotExist:
            return Response({'error':True,
                             'description':'E-mail ID is not registered with organization. Please contact admin in your organization.'
                             })
        if teamuser.active==False:
            return Response({'error':True,
                             'description':'Partner license is not active for provided E-mail ID. Please contact admin in your organization.'
                             })
        elif not self.validate_device(teamuser):
            return Response({'error': True,
                             'description': 'you have reached a limit for maximum device used.'
                             })
        '''For demo'''
        if email=='demouser@example.com':
            return Response({'error':False,
        'description':'Please verify using the OTP sent on %s.'%email
        })
        
        '''expire the last OTP and re-generate it'''
        otps=Otp.objects.filter(teamuser=teamuser,expired=False)
        for otp in otps:
            otp.expired=True
            otp.save()

        obj=Otp.objects.create(teamuser=teamuser,one_time_password=''.join(random.choice('0123456789') for i in range(6)))
        EmailThread(
            subject='Your Enpass sign-in One-Time Password',
            template_path='team/otp_confirmation.html',
            recipient_list=[teamuser],
            extra_context={'otp':obj.one_time_password,'time':obj.created_at}
        ).start()
# TODO: remove otp from description
        return Response({'error':False,
        'description':'Please verify using the OTP sent on %s.' % email
        })




'''
query: /api/signin2/
Method: POST
data: {
"organization_id": "oriental",
"email": "abi@gmail.com",
"otp" : "464665",
"device_id" : "hjsjdgfyew4378sd",
"device_name" : "OnePlus3"
}
'''

class Signin2(APIView):
    authentication_classes = ( BasicAuthentication,)
    throttle_classes = (AnonRateThrottle,UserRateThrottle)
    def create_device(self,user, device_id, device_name):
        obj,created=Device.objects.update_or_create(user=user,device_id=device_id,
                                                     defaults={'device_name': device_name},)


    def post(self,request,format=None):
        
        organization_id=request.data['organization_id']
        email=request.data['email']
        otp=request.data['otp']
        device_id=request.data.get('device_id','')
        device_name=request.data.get('device_name','')
        request.GET.get('q', '')
        if not otp:
            return Response({'error':True,'description':'OTP is required.'})
            
        team=Team.objects.get(organizationId=organization_id)
        teamuser=TeamUser.objects.get(email=email,organization=team)

        if teamuser.active==False:
            return Response({'error':True,'description':'Partner license is not active for provided E-mail ID. Please contact admin in your organization.'})
        
        '''for Demo'''
        if email=='demouser@example.com' and otp=='123456':
            obj,created= Token.objects.get_or_create(user=teamuser.user)
            return Response({'error':False,'token' : obj.key})
        try:
            Otp.objects.get(teamuser=teamuser,one_time_password=otp,expired=False)
            obj,created= Token.objects.get_or_create(user=teamuser.user)
            # TODO: remove device_id condition for final
            if device_id:
                self.create_device(teamuser,device_id,device_name)
            return Response({'error':False,'token' : obj.key})
        except Otp.DoesNotExist:
            if Otp.objects.filter(teamuser=teamuser,one_time_password=otp,expired=True).exists():
                return Response({'error':True,'description' : 'OTP has been expired.'})
            else:   
                return Response({'error':True,'description':'Incorrect OTP. Please try again.'})
                

'''
query: /api/resend_otp/
Method: POST
data: {
"organization_id": "oriental",
"email": "abi@gmail.com"
}
'''
class ResendOTP(APIView):
    authentication_classes = ( BasicAuthentication,)
    throttle_classes = (AnonRateThrottle,UserRateThrottle)
    def post(self,request,format=None):
        organization_id=request.data['organization_id']
        email=request.data['email']
        team=Team.objects.get(organizationId=organization_id)
        teamuser=TeamUser.objects.get(email=email,organization=team)
        if email=='demouser@example.com':
            return Response({'error':False,
                            'description':'Please verify using the OTP sent on %s.'%email
                    })
        
        '''expire the last OTP and re-generate it'''
        otps=Otp.objects.filter(teamuser=teamuser,expired=False)
        for otp in otps:
            otp.expired=True
            otp.save()

        obj=Otp.objects.create(teamuser=teamuser,one_time_password=''.join(random.choice('0123456789') for i in range(6)))
        EmailThread(
            subject='Your Enpass sign-in One-Time Password',
            template_path='team/otp_confirmation.html',
            recipient_list=[teamuser],
            extra_context={'otp':obj.one_time_password,'time':obj.created_at}
        ).start()

        return Response({'error':False,
        'description':'Please verify using the OTP sent on %s.'%email
        })

'''
query: /api/validate/

data: {
    "token": "2107f33fe5f5cf6be80a3d2d04f52cfe5a87d627"
}
'''

class TokenValidation(APIView):
    authentication_classes = ( BasicAuthentication,)
    def post(self,request,format=None):
        token=request.data['token']
        try:
            obj=Token.objects.get(key=token)
            return Response({'error':False,'token' : token})
        except:
            return Response({'error':True,'token' : 'Expired'})



