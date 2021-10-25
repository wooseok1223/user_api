from rest_framework import serializers
from . import models
from django.contrib.auth.hashers import make_password


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        user = models.User.objects.create(
            email=validated_data['email'],
            nickname=validated_data['nickname'],
            username=validated_data['username'],
            phone_number=validated_data['phone_number']
        )
        password = make_password(validated_data["password"])
        user.password = password
        user.save()
        return user

    class Meta:
        model = models.User
        fields = [
            'user_index',
            'email',
            'nickname',
            'password',
            'username',
            'phone_number',
            'created_at',
            'modified_at'
        ]


class AuthSerializer(serializers.ModelSerializer):
    auth_number = serializers.IntegerField(required=False)

    class Meta:
        model = models.Auth
        fields = [
            'pk',
            'phone_number',
            'auth_number',
            'created_at',
            'modified_at',
            'password_modified_at'
        ]


class LoginSerializer(serializers.ModelSerializer):
    password = serializers.CharField(read_only=True)

    class Meta:
        model = models.User
        fields = [
            'email',
            'nickname',
            'password',
            'username',
            'phone_number',
            'created_at',
            'modified_at'
        ]


class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.User
        fields = [
            'email',
            'nickname',
            'username',
            'phone_number',
            'created_at',
            'modified_at'
        ]