from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login, logout

User = get_user_model()

class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('phone', 'password')
        extra_kwargs = {'password': {'write_only':True},}

        def create(self, validated_data):
            user = User.objects.create(**validated_data)
            return user


class LoginSerializer(serializers.Serializer):
    phone = serializers.CharField()
    password = serializers.CharField(
        style = { 'input type': 'password'},trim_whitespace = False
    )

    def validate(self, data):
        print(data)
        phone = data.get('phone')
        password = data.get('password')
        if phone and password:
            if User.objects.filter(phone = phone).exists():
                print(phone, password)
                user =authenticate(request = self.context.get('request'), phone= phone , password = password)
                print(user)
            else:
                msg = {
                    'detail' : 'Phone number not found',
                    'status' : False,
                }
                raise serializers.ValidationError(msg)

            if not user:
                msg = {
                    'detail' : 'Phone number and password are not matching, Try again',
                    'status' : False,
                }
                raise serializers.ValidationError(msg, code='authorization')
        
        else:
            msg = {
                'detail' : 'Phone number and password are not found in request',
                'status' : False,
            }
            raise serializers.ValidationError(msg, code='authorization')
        data['user'] = user
        return data