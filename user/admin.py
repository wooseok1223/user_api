from django.contrib import admin
from . import models


@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['user_index', 'nickname', 'username', 'phone_number', 'email', 'created_at']
    list_display_links = ['phone_number']


@admin.register(models.Auth)
class AuthAdmin(admin.ModelAdmin):
    list_display = ['phone_number', 'auth_number', 'created_at']
    list_display_links = ['phone_number']