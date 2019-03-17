from django.urls import path
from . import views

urlpatterns = [
    path(r'h/', views.helo, name='helo'),
]