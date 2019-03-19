from django.urls import path
from . import views

urlpatterns = [
    path(r'h/', views.helo, name='helo'),
    path(r'login/', views.login, name='login'),
    path(r'mgr/', views.mgr, name='mgr'),
    path(r'category_write/', views.category_mgr, name='category_mgr'),
    path(r'category_write/del/<int:id>/', views.category_write_del),
    path(r'category_write/add/', views.category_write_add, name='category_write_add'),

]