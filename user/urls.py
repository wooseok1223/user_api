from django.urls import path
from . import views


urlpatterns = [
    path('auth/', views.AuthView.as_view(), name='auth'),
    path('signup/', views.SignView.as_view(), name='sign-up')
]
