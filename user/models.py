from django.db import models
from base.common.models import BaseModel


class User(BaseModel):
    USERNAME_FIELD = 'email'

    user_index = models.AutoField(primary_key=True, verbose_name="유저고유번호")
    email = models.EmailField(unique=True, blank=True, null=True)
    nickname = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=150)
    username = models.CharField(max_length=50)
    phone_number = models.CharField(unique=True, max_length=13, blank=True, null=True)

    class Meta:
        db_table = 'user'


class Auth(BaseModel):
    phone_number = models.CharField(unique=True, max_length=13, blank=True, null=True)
    auth_number = models.IntegerField(verbose_name='인증 번호')
    password_modified_at = models.DateTimeField(blank=True, null=True, verbose_name="비밀번호 수정일")

    class Meta:
        db_table = 'user_auth'

