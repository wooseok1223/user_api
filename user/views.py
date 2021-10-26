import os
from datetime import datetime, timedelta

import jwt
from django.contrib.auth.hashers import make_password
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from base.common import permission
from rest_framework import exceptions as exc
from rest_framework.decorators import action

from . import models, serializers
from base.common.handler import api_handler
from rest_framework.viewsets import ModelViewSet


class AuthViewSet(ModelViewSet):
    serializer_class = serializers.AuthSerializer

    phone_number = openapi.Parameter('phone_number', openapi.IN_QUERY, description='핸드폰번호', type=openapi.TYPE_STRING)
    email = openapi.Parameter('email', openapi.IN_QUERY, description='이메일', type=openapi.TYPE_STRING)
    password = openapi.Parameter('password', openapi.IN_QUERY, description='비밀번호', type=openapi.TYPE_STRING)
    auth_number = openapi.Parameter('auth_number', openapi.IN_QUERY, description='인증번호', type=openapi.TYPE_INTEGER)
    nickname = openapi.Parameter('nickname', openapi.IN_QUERY, description='닉네임', type=openapi.TYPE_STRING)
    username = openapi.Parameter('username', openapi.IN_QUERY, description='이름', type=openapi.TYPE_STRING)

    def get_queryset(self):
        auth = models.Auth.objects.all()
        return auth

    @swagger_auto_schema(manual_parameters=[phone_number])
    @api_handler
    def list(self, request, *args, **kwargs):
        """
            인증 번호 조회 api

            ---
            설명 : (SMS대용)
            ## `user/auth`
            ## 내용
                - phone_number : 010-0000-0000 (핸드폰 번호) (string)
        """
        queryset = self.filter_queryset(self.get_queryset())

        serializer = self.get_serializer(queryset, many=True)

        if len(serializer.data) == 0:
            raise exc.ValidationError("등록된 핸드폰번호가 없습니다.")

        return serializer.data

    @api_handler
    def create(self, request, *args, **kwargs):
        """
            인증 번호 초기생성 api

            ---
            설명 : (초기 생성용도(회원가입 api 진행전))
            ## `user/auth`
            ## 내용
                - phone_number : 010-0000-0000 (핸드폰 번호) (string)
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return serializer.data

    @swagger_auto_schema(manual_parameters=[phone_number, auth_number])
    @api_handler
    @action(detail=False, methods=["get"], url_path="auth_check")
    def auth_check(self, request):
        """
           인증 번호 확인 api

           ---
           설명 : (프론트에서 문자로 온 인증번호 입력하는 용도 - 원래목적)
           ## `user/auth/auth_check`
           ## 내용
               - phone_number : 010-0000-0000 (핸드폰 번호) (string)
               - auth_number : 4212 (인증번호) (integer) GET user/auth 로 가져온값

        """
        phone_number = request.GET.get("phone_number")
        auth_number = request.GET.get("auth_number")

        auth = models.Auth.check_auth_number(phone_number, auth_number)
        serializer = serializers.AuthSerializer(auth)

        return serializer.data

    @api_handler
    @action(detail=False, methods=["put"], url_path="change", url_name='change')
    def auth_changed(self, request):
        """
            인증 번호 발급 api

            ---
            설명 : (비밀번호 변경, 인증번호 확인 api에서 사용)
            ## `user/auth/change`
            ## 내용
                - phone_number : 010-0000-0000 (핸드폰 번호) (string)
        """
        phone_number = request.data.get("phone_number", None)

        try:
            auth = models.Auth.objects.get(phone_number=phone_number)
        except:
            raise exc.ValidationError("초기인증 발급 후 신청해주세요")

        auth.password_modified_at = datetime.now()

        auth.save()

        return {"auth_number": auth.auth_number}


class SignView(generics.CreateAPIView):
    """
        회원가입 api

        ---
        설명 : (인증번호 5분 초과 하거나 일치하지 않으면 가입 불가)
        ## `user/signup/`
        ## 내용
            - email: test@test.com (이메일) (string)
            - password : password (비밀번호) (string)
            - phone_number : 010-0000-0000 (핸드폰 번호) (string)
            - nickname : 테스트 (닉네임) (string)
            - username : 서우석 (유저이름) (string)
            - auth_number : 4212 (인증번호) (integer) GET user/auth 로 가져온값
    """
    model = models.User
    serializer_class = serializers.SignupSerializer

    @api_handler
    def create(self, request, *args, **kwargs):
        models.Auth.check_auth_number(request.data["phone_number"], request.data["auth_number"])

        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            self.perform_create(serializer)
        else:
            raise exc.ValidationError(serializer.errors)

        return serializer.data


class LoginView(generics.CreateAPIView):
    """
        로그인 api

        ---
        설명 : (JWT token 인증 로그인 방식 적용)
        ## `user/login/`
        ## 내용
            ## 이메일로 로그인
            - email: test@test.com (이메일) (string)
            - password : password (비밀번호) (string)

            ## 폰번호로 로그인
            - phone_number : 010-0000-0000 (핸드폰 번호) (string)
            - password : password (비밀번호) (string)

            ## 닉네임으로 로그인
            - nickname : 테스트 (닉네임) (string)
            - password : password (비밀번호) (string)
    """
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
    """
        프로필 조회 api

        ---
        설명 : 로그인 토큰값이 있어야 조회가능, 토큰값 디코드를 통해서 user pk로 로그인
        ## `user/profile/`
        ## 내용
            ## 해더 정보
            - TOKEN: 로그인 해서 나온 토큰값
    """
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
    """
        비밀번호 변경 api

        ---
        설명 : (인증번호 5분 초과 하거나 일치하지 않으면 가입 불가) 인증번호가 일치 했을때 새로 입력한 비밀번호로 교체
        ## `user/profile/{user_index}/changed`
        ## 내용
            ## 해더 정보
            - TOKEN: 로그인 해서 나온 토큰값

            ## 파라미터 정보
            - phone_number : 010-0000-0000 (핸드폰 번호) (string)
            - password : password (비밀번호) (string)
            - auth_number : 4212 (인증번호) (integer) user/auth 로 가져온값
    """
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
