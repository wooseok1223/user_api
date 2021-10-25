import os
from datetime import datetime, timedelta

import jwt
from django.contrib.auth.hashers import make_password
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
import json

from . import models


class AuthTest(APITestCase):
    def tearDown(self):
        models.Auth.objects.all().delete()

    def setUp(self):
        params = {
            "phone_number": "010-0000-0000"
        }

        url = reverse("auth-list")

        self.assertEqual(url, "/user/auth/")
        res = self.client.post(url, data=json.dumps(params), content_type="application/json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        res = res.json()

        self.auth_number = res.get("result").get("auth_number")

    def test_auth_success(self):
        params = {
            "phone_number": "010-0000-0000"
        }

        url = reverse("auth-list")

        self.assertEqual(url, "/user/auth/")
        res = self.client.get(url, query_string=params)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        res = res.json()

        auth_number = res.get("result")[0].get("auth_number")

        self.assertEqual(self.auth_number, auth_number)


class SignUpTest(AuthTest):
    def tearDown(self):
        models.User.objects.all().delete()

    def test_signup_success(self):
        auth_number = self.auth_number

        params = {
            "email": "test@gmail.com",
            "password": "password",
            "nickname": "test_user",
            "username": "서우석",
            "phone_number": "010-0000-0000",
            "auth_number": auth_number
        }

        url = reverse("sign-up")

        self.assertEqual(url, "/user/signup/")
        res = self.client.post(url, data=json.dumps(params), content_type="application/json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)


class TestWithUser(APITestCase):
    def tearDown(self):
        models.Auth.objects.all().delete()
        models.User.objects.all().delete()

    def setUp(self):
        params = {
            "phone_number": "010-0000-0000"
        }

        url = reverse("auth-list")

        self.assertEqual(url, "/user/auth/")
        res = self.client.post(url, data=json.dumps(params), content_type="application/json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        res = res.json()

        auth_number = res.get("result").get("auth_number")

        params = {
            "email": "test@gmail.com",
            "password": "password",
            "nickname": "test_user",
            "username": "서우석",
            "phone_number": "010-0000-0000",
            "auth_number": auth_number
        }

        url = reverse("sign-up")

        self.assertEqual(url, "/user/signup/")
        res = self.client.post(url, data=json.dumps(params), content_type="application/json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.auth_number = auth_number

        res = res.json()

        payload = {
            "iss": "user_api",
            "user_index": res.get("result").get("user_index"),
            "exp": datetime.now() + timedelta(seconds=60 * 60 * 24),
        }

        jwt_encode = jwt.encode(payload=payload, key=os.environ["SECRET_KEY"], algorithm="HS256")
        token = jwt_encode.decode("utf-8")

        self.user = res.get("result")
        self.token = token


class LoginTest(TestWithUser):
    def run_api(self, params):
        url = reverse("login")

        self.assertEqual(url, "/user/login/")
        res = self.client.post(url, data=json.dumps(params), content_type="application/json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        res = res.json()

        self.user_info = res.get("result").get("user_info")
        self.token = res.get("result").get("token")

    def test_login_phone_number_success(self):
        params = {
            "phone_number": "010-0000-0000",
            "password": "password"
        }

        self.run_api(params)

    def test_login_nickname_success(self):
        params = {
            "nickname": "test_user",
            "password": "password"
        }

        self.run_api(params)

    def test_login_email_success(self):
        params = {
            "email": "test@gmail.com",
            "password": "password"
        }

        self.run_api(params)


class ProfileTest(TestWithUser):

    def test_get_profile_success(self):
        url = reverse("profile")

        self.assertEqual(url, "/user/profile/")

        header = {"HTTP_TOKEN": self.token}

        res = self.client.get(url, **header)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_profile_password_changed_success(self):
        url = reverse("auth-change")

        params = {
            "phone_number": "010-0000-0000"
        }

        self.assertEqual(url, f"/user/auth/change/")

        res = self.client.put(url, data=json.dumps(params), content_type="application/json")

        res = res.json()

        auth_number = res.get("result").get("auth_number")
        user_index = self.user.get("user_index")

        url = reverse("password-change", kwargs={'pk': user_index})

        self.assertEqual(url, f"/user/profile/{user_index}/changed/")

        header = {"HTTP_TOKEN": self.token}

        params["auth_number"] = auth_number
        params["username"] = self.user.get("username")
        params["email"] = self.user.get("email")
        params["nickname"] = self.user.get("nickname")
        params["password"] = "qwer1234"

        res = self.client.put(url, data=json.dumps(params), content_type="application/json",  **header)
        self.assertEqual(res.status_code, status.HTTP_200_OK)


