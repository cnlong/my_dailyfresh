from django.urls import path
from . import views

urlpatterns = [
    path('register', views.register, name='register'),  # 注册
    # path('register_handle', views.register_handle, name='register_handle'),  # 注册处理
]
