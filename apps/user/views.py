from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def index(request):
    return HttpResponse('用户首页')

# /user/register
def register(request):
    """注册页面"""
    return render(request, 'register.html')