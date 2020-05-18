from django.urls import path, re_path
from . import views
from .views import RegisterView,ActiveView,LoginView

urlpatterns = [
    path('register', RegisterView.as_view(), name='register'),  # 注册
    # path('active/<str: token>', ActiveView.as_view(), name='active'),  # 激活
    # 带参数的url，个人觉得还是re_path还有一些
    re_path(r'^active/(?P<token>.*)$', ActiveView.as_view(), name='active'),
    path('login', LoginView.as_view(), name='login'),  # 登录
    # path('register', views.register, name='register'),  # 注册
    # path('register_handle', views.register_handle, name='register_handle'),  # 注册处理
]
