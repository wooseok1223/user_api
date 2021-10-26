from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.permissions import AllowAny
from django.conf.urls import url

schema_url_patterns = [path("user/", include("user.urls"), name="user")]
schema_view = get_schema_view(
    openapi.Info(title="User api of wooseok", default_version='v1', terms_of_service="https://www.google.com/policies/terms/", ),
    public=True, permission_classes=(AllowAny,), patterns=schema_url_patterns, )

urlpatterns = [
    path('admin/', admin.site.urls),
    path("user/", include("user.urls"), name="user"),
    url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
