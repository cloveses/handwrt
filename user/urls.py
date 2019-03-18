from django.urls import path
from . import views

urlpatterns = [
    path(r'h/', views.helo, name='helo'),
    path(r'login/', views.login, name='login'),
]