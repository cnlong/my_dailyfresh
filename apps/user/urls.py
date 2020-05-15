from django.urls import path
from . import views
from .views import RegisterView,ActiveView,LoginView

urlpatterns = [
    path('register', RegisterView.as_view(), name='register'),  # 注册
    path('active/<int: token>', ActiveView.as_view(), name='active'),  # 激活
    path('login', LoginView.as_view(), name='login'),  # 登录
    # path('register', views.register, name='register'),  # 注册
    # path('register_handle', views.register_handle, name='register_handle'),  # 注册处理
]
