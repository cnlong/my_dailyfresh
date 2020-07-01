from django.urls import path, re_path
from .views import *
app_name = 'goods'
urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('goods/<int:goods_id>/', DetailView.as_view(), name='detail'),
    # re_path(r"^goods/(?P<goods_id>\d+)$", DetailView.as_view(), name='detail'),
    path('list/<int:type_id>/<int:page>/', ListView.as_view(), name='list'),
]
