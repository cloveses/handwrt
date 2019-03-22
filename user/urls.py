from django.urls import path
from . import views

urlpatterns = [
    path(r'h/', views.helo, name='helo'),
    path(r'login/', views.login, name='login'),
    path(r'mgr/', views.mgr, name='mgr'),
    path(r'category_write/', views.category_mgr, name='category_mgr'),
    path(r'category_write/del/<int:id>/', views.category_write_del),
    path(r'category_write/add/', views.category_write_add, name='category_write_add'),
    path(r'category_content/add/', views.category_content_add, name='category_content_add'),
    path(r'user_mgr/', views.user_mgr, name='user_mgr'),
    path(r'register/', views.register, name='register'),
    path(r'union_reg/', views.union_reg, name='union_reg'),
    path(r'union_mgr/', views.union_mgr, name='union_mgr'),
    path(r'union_owner_mgr/', views.union_owner_mgr, name='union_owner_mgr'),
    path(r'union_info/', views.union_info, name='union_info'),

]