from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import User
from django.views import View
# 用户信息加解密的类
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
# 加密过期异常
from itsdangerous import SignatureExpired
import re
from django.conf import settings
from django.core.mail import send_mail
# 使用celery任务发送邮件
from celery_tasks.tasks import send_register_active_email

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


class RegisterView(View):
    """注册类视图"""
    def get(self, request):
        """处理get请求的实例方法"""
        # 显示注册页面
        return render(request, 'register.html')

    def post(self, request):
        """处理post请求的实例方法"""
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
        # 发送激活邮件，包含激活链接：http://127.0.0.1:8000/user/active/1
        # 激活链接中需要包含用户的身份信息(例如用户的id)
        # 为防止其他人猜测激活链接，向服务器不断请求，所以需要对激活链接中的用户身份进行加密

        # 加密用户的身份信息，生成激活的token
        # 使用项目settings.py中的SECRET_KEY作为加密的密钥
        # 创建加密对象，过期时间为3600秒
        serializer = Serializer(settings.SECRET_KEY, 3600)
        # 定义加密的信息，使用之前创建好的用户的id
        info = {'confirm': user.id}
        # 加密，返回的是字节流的数据，转换为字符串
        token = serializer.dumps(info).decode('utf-8')


        # 发送邮件
        # # 邮件主题
        # subject = '天天生鲜欢迎信息'
        # # 邮件正文
        # message = ''
        # # 因为包含html的内容，需要通过html_message进行参数传递
        # html_message = '<h1>%s, 欢迎您成为天天生鲜注册会员</h1>请点击下面链接激活您的账户<br/><a href="http://127.0.0.1:8000/user/active/%s">http://127.0.0.1:8000/user/active/%s</a>' %(username, token, token)
        # # 发件人
        # sender = settings.EMAIL_FROM
        # # 收件人列表
        # receiver = [email]
        # send_mail(subject, message, sender, receiver, html_message=html_message)
        # 使用celery任务发送邮件
        send_register_active_email.delay(email, username, token)


        # 返回应答，跳转到首页
        # 首页后续修改，先返回一个页面
        return HttpResponse('首页')


class ActiveView(View):
    """用户激活的类视图"""
    def get(self, request, token):
        """根据用户访问激活页面和传递的用户信息进行解密，解密成功即可激活"""
        # 进行解密，获取要激活的用户信息
        serializer = Serializer(settings.SECRET_KEY, 3600)
        try:
            info = serializer.loads(token)
            # 获取解密出来的用户id
            user_id = info['confirm']
            # 根据id获取用户信息，然后改变数据库字段，激活
            user = User.objects.get(id=user_id)
            user.is_active = 1
            user.save()
            # 激活完成，跳转到登录页面
            # 重定向，使用反向解析到登录页
            # return redirect(reversed('user:login'))
            return HttpResponse('登录页')
        except SignatureExpired as e:
            # 激活链接已过期
            return HttpResponse('链接已过期')



# /user/login
class LoginView(View):
    """登录页类视图"""
    def get(self, request):
        """显示登录页"""
        return HttpResponse('登录页')