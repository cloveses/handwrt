from django.urls import path
from . import views

urlpatterns = [
    path('h/', views.helo, name='helo'),
    path('login/', views.login, name='login'),
    path('mgr/', views.mgr, name='mgr'),
    path('category_write/', views.category_mgr, name='category_mgr'),
    path('category_write/del/<int:id>/', views.category_write_del),
    path('category_content/del/<int:id>/', views.category_content_del),
    path('category_write/add/', views.category_write_add, name='category_write_add'),
    path('category_content/add/', views.category_content_add, name='category_content_add'),
    path('user_mgr/', views.user_mgr, name='user_mgr'),
    path('register/', views.register, name='register'),
    path('union_reg/', views.union_reg, name='union_reg'),
    path('union_mgr/', views.union_mgr, name='union_mgr'),
    path('union_owner_mgr/', views.union_owner_mgr, name='union_owner_mgr'),
    path('union_info/', views.union_info, name='union_info'),
    path('handwrt_mgr/', views.handwrt_mgr, name='handwrt_mgr'),
    path('get_handwrt_writes/', views.get_handwrt_writes, name='get_handwrt_writes'),
    path('get_handwrt_contents/', views.get_handwrt_contents, name='get_handwrt_contents'),
    path('get_handwrt_category_supers/', views.get_handwrt_category_supers, name='get_handwrt_category_supers'),
    path('display/', views.display, name='display'),
    path('search/', views.search, name='search'),
    path('personal/', views.personal, name='personal'),
    path('user_info/', views.user_info, name='user_info'),
    path('get_handwrts_union/<int:unid>/', views.get_handwrts_union, name='get_handwrts_union'),
    path('person_handwrt_mgr/', views.person_handwrt_mgr, name='person_handwrt_mgr'),
    path('attend_union/', views.attend_union, name='attend_union'),
    path('page_test/<int:page>/', views.page_test, name='page_test'),

]