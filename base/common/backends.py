import os

import jwt
from django.apps import apps
from rest_framework import exceptions as exc
from rest_framework.authentication import BaseAuthentication


class Token(BaseAuthentication):
    def authenticate(self, request):

        access_token = request.META.get("HTTP_TOKEN", None)  # header: {'TOKEN' or 'token': token}

        if not access_token or access_token == "undefined":
            return None
        try:
            decoded = jwt.decode(access_token, key=os.environ["SECRET_KEY"], algorithm="HS256")
        except Exception as ex:
            print(ex)
            return None

        user = apps.get_model("user", "User")
        user_index = decoded.get("user_index")

        try:
            user = user.objects.get(pk=user_index)

            user.is_authenticated = True

            return (user, True)

        except user.DoesNotExist:
            raise exc.AuthenticationFailed("authentication failed")