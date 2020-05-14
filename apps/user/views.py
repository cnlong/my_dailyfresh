from django.shortcuts import render
from django.http import HttpResponse
from .models import User
import re

# Create your views here.

# /user/register
def register(request):
    """注册页面"""
    if request.method == 'Get':
        # 显示注册页面
        return render(request, 'register.html')
    else:
        # 接收数据
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        email = request.POST.get('email')
        allow = request.POST.get('allow')
        # 进行数据校验
        # all()判断内部元素是否都存在，都存在为真，不都存在为假
        if not all([username, password, email]):
            # 数据不完整，返回注册页面，并提示报错信息
            return render(request, 'register.html', {'errmsg': '数据不完整'})

        # 校验邮箱
        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'register.html', {'errmsg': '邮箱不合法'})

        # 检查勾选框是否勾选，如果勾选，传过来的值为“on”
        if allow != 'on':
            return render(request, 'register.html', {
                'errmsg': '请同意协议'
            })

        # 校验用户名是否重复
        try:
            user = User.objects.get(username=username)
        # 查询不到会抛出异常，捕获异常即可
        except User.DoesNotExist:
            # 用户名不存在
            user = None
        if user:
            # 用户名已存在
            return render(request, 'register.html', {'error_msg': '用户名已存在'})
        # 进行业务处理，进行用户注册
        # 通过User模型类存储创建的新用户
        # 因为是继承自Django自身的认证系统，所以用户数据写入直接参考其方法即可
        user = User.objects.create_user(username, password, email)
        # 刚刚注册好的用户，不能直接激活状态，自行改为未激活状态
        user.is_active = 0
        user.save()

        # 返回应答，跳转到首页
        # 首页后续修改，先返回一个页面
        return HttpResponse('首页')

# def register_handle(request):
#     """注册处理"""
#     # 接收数据
#     username = request.POST.get('user_name')
#     password = request.POST.get('pwd')
#     email = request.POST.get('email')
#     allow = request.POST.get('allow')
#     # 进行数据校验
#     # all()判断内部元素是否都存在，都存在为真，不都存在为假
#     if not all([username, password, email]):
#         # 数据不完整，返回注册页面，并提示报错信息
#         return render(request, 'register.html', {'errmsg': '数据不完整'})
#
#     # 校验邮箱
#     if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
#         return render(request, 'register.html', {'errmsg': '邮箱不合法'})
#
#     # 检查勾选框是否勾选，如果勾选，传过来的值为“on”
#     if allow != 'on':
#         return render(request, 'register.html', {
#             'errmsg': '请同意协议'
#         })
#
#     # 校验用户名是否重复
#     try:
#         user = User.objects.get(username=username)
#     # 查询不到会抛出异常，捕获异常即可
#     except User.DoesNotExist:
#         # 用户名不存在
#         user = None
#     if user:
#         # 用户名已存在
#         return render(request, 'register.html', {'error_msg': '用户名已存在'})
#     # 进行业务处理，进行用户注册
#     # 通过User模型类存储创建的新用户
#     # 因为是继承自Django自身的认证系统，所以用户数据写入直接参考其方法即可
#     user = User.objects.create_user(username, password, email)
#     # 刚刚注册好的用户，不能直接激活状态，自行改为未激活状态
#     user.is_active = 0
#     user.save()
#
#
#     # 返回应答，跳转到首页
#     # 首页后续修改，先返回一个页面
#     return HttpResponse('首页')

