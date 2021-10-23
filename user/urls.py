from django.urls import path, include
from rest_framework.routers import SimpleRouter

from . import views

router = SimpleRouter(trailing_slash=True)

router.register(r"auth", views.AuthViewSet, basename="auth")

urlpatterns = [
    path('', include(router.urls)),

    path('signup/', views.SignView.as_view(), name='sign-up'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/<int:pk>/changed/', views.PwdChangedView.as_view(), name='password-change')
]
