from rest_framework import serializers
from .models import User
from django.contrib.auth import password_validation
from rest_framework import validators, exceptions


class RegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[validators.UniqueValidator(queryset=User.objects.all())],
        write_only=True,   
    )
    password = serializers.CharField(
        required=True,
        validators=[password_validation.validate_password],
        write_only=True,
    )
    password2 = serializers.CharField(
        required=True,
        write_only=True,
    )
    
    class Meta:
        model = User
        fields = (
            'first_name', 
            'last_name',
            'username',
            'email',
            'password',
            'password2',
        )
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True}
        }
        
    def validate(self, attrs):
        if attrs.get('password') != attrs.get('password2'):
            raise exceptions.ValidationError({"password": "The two passwords do not match."})
        return attrs
        
    def create(self, validated_data):
        user = User.objects.create(
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user    