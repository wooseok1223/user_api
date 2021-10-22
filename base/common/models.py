from django.db import models


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name="생성일")
    modified_at = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name="수정일")

    class Meta:
        abstract = True
