from random import randint
from datetime import timedelta
from django.utils.timezone import now
from django.contrib.auth.hashers import check_password
from django.db import models
from base.common.models import BaseModel
from rest_framework import exceptions as exc


class User(BaseModel):
    USERNAME_FIELD = 'email'

    user_index = models.AutoField(primary_key=True, verbose_name="유저고유번호")
    email = models.EmailField(unique=True, verbose_name="email")
    nickname = models.CharField(max_length=50, unique=True, verbose_name="nickname")
    password = models.CharField(max_length=150)
    username = models.CharField(max_length=50)
    phone_number = models.CharField(unique=True, max_length=13)

    class Meta:
        db_table = "tb_user"
        app_label = "user"

    @classmethod
    def user_filter(cls, param):
        nickname = param.get("nickname", None)
        email = param.get("email", None)
        phone_number = param.get("phone_number", None)
        password = param.get("password", None)

        if (not nickname and not email and not phone_number) or not password:
            raise exc.ParseError("필수 파라미터값이 없습니다.")

        try:
            if nickname:
                obj = cls.objects.get(nickname=nickname)
            elif email:
                obj = cls.objects.get(email=email)
            elif phone_number:
                obj = cls.objects.get(phone_number=phone_number)
            else:
                raise exc.ValidationError("존재하지 않는 유저입니다.")
        except:
            raise exc.ValidationError(f'존재하지 않는 유저입니다.')

        if not check_password(password, obj.password):
            raise exc.NotAuthenticated("패스워드가 일치하지 않습니다.")

        return obj


class Auth(BaseModel):
    phone_number = models.CharField(unique=True, max_length=13)
    auth_number = models.IntegerField(verbose_name='인증 번호')
    password_modified_at = models.DateTimeField(blank=True, null=True, verbose_name="비밀번호 수정일")

    class Meta:
        db_table = 'tb_auth'
        app_label = "user"

    def save(self, *args, **kwargs):
        self.auth_number = randint(1000, 10000)
        super().save(*args, **kwargs)

    @classmethod
    def check_auth_number(cls, p_num, c_num):
        time_limit = now() - timedelta(minutes=5)

        try:
            result = cls.objects.get(
                phone_number=p_num,
                auth_number=c_num,
                modified_at__gte=time_limit
            )
        except:
            raise exc.ParseError("인증번호가 올바르지 않거나 시간이 초과되었습니다.")

        return result




