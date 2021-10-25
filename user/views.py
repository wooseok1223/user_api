import os
from datetime import datetime, timedelta

import jwt
from django.contrib.auth.hashers import make_password
from rest_framework import generics
from base.common import permission
from rest_framework import exceptions as exc
from rest_framework.decorators import action

from . import models, serializers
from base.common.handler import api_handler
from rest_framework.viewsets import ModelViewSet


class AuthViewSet(ModelViewSet):
    serializer_class = serializers.AuthSerializer

    def get_queryset(self):
        auth = models.Auth.objects.all()
        return auth

    @api_handler
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        serializer = self.get_serializer(queryset, many=True)

        return serializer.data

    @api_handler
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return serializer.data

    @api_handler
    @action(detail=False, methods=["get"], url_path="auth_check")
    def auth_check(self, request):
        phone_number = request.GET.get("phone_number")
        auth_number = request.GET.get("auth_number")

        auth = models.Auth.check_auth_number(phone_number, auth_number)
        serializer = serializers.AuthSerializer(auth)

        return serializer.data

    @api_handler
    @action(detail=False, methods=["put"], url_path="change", url_name='change')
    def auth_changed(self, request):
        phone_number = request.data.get("phone_number", None)

        auth = models.Auth.objects.get(phone_number=phone_number)

        auth.password_modified_at = datetime.now()

        auth.save()

        return {"auth_number": auth.auth_number}


class SignView(generics.CreateAPIView):
    model = models.User
    serializer_class = serializers.SignupSerializer

    @api_handler
    def create(self, request, *args, **kwargs):
        models.Auth.check_auth_number(request.data["phone_number"], request.data["auth_number"])

        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            self.perform_create(serializer)
        else:
            print(serializer.errors)

        return serializer.data


class LoginView(generics.CreateAPIView):
    model = models.User
    serializer_class = serializers.LoginSerializer

    @api_handler
    def create(self, request, *args, **kwargs):
        obj = models.User.user_filter(request.data)

        payload = {
            "iss": "user_api",
            "user_index": obj.user_index,
            "exp": datetime.now() + timedelta(seconds=60 * 60 * 24),
        }

        jwt_encode = jwt.encode(payload=payload, key=os.environ['SECRET_KEY'], algorithm="HS256")
        token = jwt_encode.decode("utf-8")

        return {
            "token": token,
            "expire_time": datetime.now() + timedelta(seconds=60 * 60 * 24),
            "user_info": {
                "phone_number": obj.phone_number,
                "nickname": obj.nickname,
                "email": obj.email
            }
        }


class ProfileView(generics.ListAPIView):
    queryset = models.User.objects.all()
    serializer_class = serializers.ProfileSerializer
    permission_classes = [permission.UserCheck]

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(pk=self.request.user.pk)
        return qs

    @api_handler
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        serializer = self.get_serializer(queryset, many=True)

        return serializer.data


class PwdChangedView(generics.UpdateAPIView):
    queryset = models.User.objects.all()
    serializer_class = serializers.SignupSerializer
    permission_classes = [permission.UserCheck]

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(pk=self.request.user.pk)
        return qs

    @api_handler
    def update(self, request, *args, **kwargs):

        phone_number = request.data.get("phone_number")
        auth_number = request.data.get("auth_number")
        password = request.data.get("password")

        # 전화번호 인증
        auth = models.Auth.check_auth_number(phone_number, auth_number)

        # 인증값 이상 없을시 패스워드 변경 진행
        if auth:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()

            send_param = {
                "phone_number": phone_number,
                "auth_number": auth_number,
                "password": make_password(password),
                "username": instance.username,
                "nickname": instance.nickname,
                "email": instance.email
            }

            serializer = self.get_serializer(instance, data=send_param, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            return serializer.data

        raise exc.ValidationError("인증을 해주세요")

