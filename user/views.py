from random import randint

from rest_framework import generics
from rest_framework import exceptions as exc
from . import models, serializers
from base.common.handler import api_handler


class SignView(generics.CreateAPIView):
    model = models.User
    serializer_class = serializers.SignupSerializer

    @api_handler
    def create(self, request, *args, **kwargs):

        auth = models.Auth.objects.get(phone_number=request.data["phone_number"])
        if auth.auth_number != int(request.data["auth_number"]):
            print(auth.auth_number)
            raise exc.ParseError("인증번호가 올바르지 않습니다.")

        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            self.perform_create(serializer)
        else:
            print(serializer.errors)

        return serializer.data


class AuthView(generics.ListCreateAPIView):
    queryset = models.Auth.objects.all()
    serializer_class = serializers.AuthSerializer

    @api_handler
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        serializer = self.get_serializer(queryset, many=True)

        return serializer.data

    @api_handler
    def create(self, request, *args, **kwargs):
        send_data = request.data.copy()
        auth_number = randint(1000, 10000)
        send_data["auth_number"] = auth_number
        serializer = self.get_serializer(data=send_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return serializer.data

