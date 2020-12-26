from django.shortcuts import render

from rest_framework import permissions, status, generics 
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import User, PhoneOTP
from django.shortcuts import get_object_or_404
import random
from .serializer import CreateUserSerializer, LoginSerializer

from knox.views import LoginView as KnoxLoginView
from knox.auth import TokenAuthentication
from django.contrib.auth import authenticate, login, logout


class ValidatePhoneSendOTP(APIView):


    def post(self,request, *args, **kwargs):
        phone_number = request.data.get('phone')
        if phone_number:
            phone = str(phone_number)
            user = User.objects.filter(phone__iexact = phone)
            if user.exists():
                return Response({
                    'status': False,
                    'detail': 'phone number already exist'
                })
            else:
                key = send_otp(phone)
                if key:
                    old = PhoneOTP.objects.filter(phone__iexact = phone)
                    if old.exists():
                        old = old.first()
                        count = old.count
                        if count > 5:
                            return Response({
                                'status': False,
                                'details': 'Sending otp error. Limit exceed.  Please contact customer Support'
                            })
                        old.count = count + 1
                        old.save()
                        print("Count increased", count)
                        return Response({
                            'status': True,
                            'detail': 'OTP sent successfully',
                            # Below line Need to be remover after testing
                            'otp'   : 'your otp is ' + str(old.otp)
                        })
                    else:
                        PhoneOTP.objects.create(
                            phone = phone,
                            otp = key,
                            
                        )
                        return Response({
                            'status': True,
                            'detail': 'OTP sent successfully',
                            # Below line Need to be remover after testing
                            'otp'   : 'your otp is ' + str(key)
                        })
                else:
                    return Response({
                        'status': False,
                        'detail': 'Sending OTP error.'
                    })
        else:
            return Response({
                'status': False,
                'detail': 'Phone number is not given in post request'
            })

def send_otp(phone):
    if phone:
        key = random.randint(999,9999)
        return key
    else:
        return False


class ValidateOTP(APIView):

    def post(self,request, *args, **kwargs):
        phone = request.data.get('phone', False)
        otp_sent = request.data.get('otp', False)

        if phone and otp_sent:
            old = PhoneOTP.objects.filter(phone__iexact = phone)
            if old.exists():
                old = old.first()
                otp = old.otp
                if str(otp_sent) == str(otp):
                    old.validated = True
                    old.save()
                    return Response({
                        'status': True,
                        'detail': 'OTP Matched. Please proceed for registration'
                    })
                
                else:
                    return Response({
                        'status': False,
                        'detail': 'OTP INCORRECT'
                    })
            else:
                return Response({
                    'status': False,
                    'detail': 'First proceed via sending otp request'
                })
        else:
            return Response({
                'status': False,
                'detail': 'Please provide both phone and otp for validation'
            })


class Register(APIView):
    def post(self,request, *args, **kwargs):
        phone = request.data.get('phone', False)
        password = request.data.get('password', False)

        if phone and password:
            old = PhoneOTP.objects.filter(phone__iexact = phone)
            if old.exists():
                old = old.first()
                validated = old.validated
                
                if validated:
                    temp_data = {
                        'phone' : phone,
                        'password' : password
                    }
                    
                    serializer = CreateUserSerializer(data = temp_data)
                    serializer.is_valid(raise_exception = True)
                    # user = serializer.save()
                    user = User.objects.create_user(phone, password)
                    old.delete()
                    return Response({
                        'status': True,
                        'detail': 'Account created'
                    })
                
                else:
                    return Response({
                        'status': False,
                        'detail': "OTP haven't verified. First do that step"
                    })


            else:
                return Response({
                    'status': False,
                    'detail': 'Please verify phone first'
                })

        else:
            return Response({
                'status': False,
                'detail': 'Both phone and password are not sent'
            })


class LoginAPI(KnoxLoginView):
    permission_classes = (permissions.AllowAny, )

    def post(self,request, format = None):
        serializer = LoginSerializer(data = request.data)
        serializer.is_valid(raise_exception = True)
        user = serializer.validated_data['user']
        login(request, user)
        return super().post(request, format=None)






#Noida - project experiment 
def visitor_ip_address(request):

    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
import uuid 
class UserRequest(APIView):

    def post(self,request, *args, **kwargs):
        user_id = uuid.uuid4().hex[:6].lower()
        print("\n user id: ",user_id)
        print(request.data)
        print(request.headers)
        ip_address = visitor_ip_address(request)
        print("client ip address: ",ip_address)
        return Response({
                'status': True,
                'detail': request.headers,
                'method': request.method,
                'X-Forwarded-For': ip_address
                # 'X-Forwarded-Port': request.headers['PORT']
            })