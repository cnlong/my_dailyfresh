from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse
from .models import User, Address
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
# 用户认证
from django.contrib.auth import authenticate, login
# 用户登录验证
from django.contrib.auth.mixins import LoginRequiredMixin
# 通过验证的用户退出函数
from django.contrib.auth import logout

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
        user = User.objects.create_user(username=username, password=password, email=email)
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
        # 重新登录的时候，判断上次登录是否记住用户名
        if 'username' in request.COOKIES:
            username = request.COOKIES.get('username')
            checked = 'checked'
        else:
            username = ''
            checked = ''
        return render(request, 'login.html', {'username': username, 'checked': checked})

    def post(self, request):
        """接收表单请求，登录校验"""
        # 接收数据
        username = request.POST.get('username')
        password = request.POST.get('pwd')
        # 校验数据，检验是否提交了用户名或者密码
        # all函数判断给定的可迭代对象是否都为True
        if not all([username, password]):
            return render(request, 'login.html', {'errmg': '数据不完整'})
        # 业务校验：登录校验
        # 根据用户名及密码验证，返回验证结果
        user = authenticate(username=username, password=password)
        # 验证通过返回一个User对象，即从数据库中查询出来的对象，验证失败返回None
        if user is not None:
            # 用户名密码验证通过，再判断用户是否激活
            if user.is_active:
                # 用户已激活
                # 记录用户的登录状态,将用户ID保存至当前session中
                login(request, user)
                # 登录成功后，获取登录后跳转的地址，这个值再直接登录页面没有，只有从用户中心跳转过来的登录页面才有
                # 表单数据由POST提交，url参数由GET提交
                # 如果直接登录，获取到的值为none,所以需要给一个默认值，默认跳转到首页
                next_url = request.GET.get('next', reverse('goods:index'))
                response = redirect(next_url)
                # 判断是否需要记住用户名，根据勾选框的值
                remember = request.POST.get('remember')
                if remember == 'on':
                    print('设置cookies')
                    # 勾选了，则返回on，并向返回页面中传入cookie
                    response.set_cookie('username', username, max_age=7*24*3600)
                else:
                    # 不勾选，则删除该cookie
                    response.delete_cookie('username')
                # 跳转到首页
                return response
            else:
                # return render(request, 'login.html', {'errmsg': '用户未激活'})
                return HttpResponse('用户未激活')
        else:
            return render(request, 'login.html', {'errmsg': '用户名或密码错误'})
        # 返回应答


class LogoutView(View):
    """退出登录"""
    # 退出登录，清除用户的所有会话数据
    def get(self, request):
        logout(request)
        # 退出之后跳转到首页
        return redirect(reverse('goods:index'))


# /user
class UserInfoView(LoginRequiredMixin, View):
    """用户中心-信息页"""
    def get(self, request):
        """显示"""
        # request.user
        # 除了给模板传递模板变量之外，django框架会把request.user也传给模板
        # 就可以直接在模板文件中判断该属性，然后改变模板文件的样式
        # 如果当前没有用户登录，这个属性将会被设置为 AnonymousUser
        # 如果当前有用户登录，这个属性将会被设置为User 实例
        # request.user.is_authenticated判断用户是否验证，未登录则为false，登录则为true

        # 1.获取用户的个人信息

        # 2.获取用户的历史浏览记录

        # 传入page=user，模板文件根据这个变量，设置链接的class属性
        return  render(request, 'user_center_info.html', {'page': 'user'})


# /user/order
class UserOrderView(LoginRequiredMixin, View):
    """用户中心-订单页"""
    def get(self, request):
        """显示"""
        # 1.获取用户的订单信息

        # 传入page=order，模板文件根据这个变量，设置链接的class属性
        return  render(request, 'user_center_order.html', {'page': 'order'})


# /user/address
class AddressView(LoginRequiredMixin, View):
    """用户中心-地址页"""
    def get(self, request):
        """显示"""
        # 1.获取用户的默认收货地址
        # 获取登录后的用户对象
        user = request.user
        # 根据用户对象，查询该对象的默认收货地址，如果存在收货地址则返回，不存在，则设置为NONE
        try:
            address = Address.objects.get(user=user, is_default=True)
        except Address.DoesNotExist:
            address = None
        # 传入page=address，模板文件根据这个变量，设置链接的class属性
        return render(request, 'user_center_site.html', {'page': 'address', 'address': address})

    def post(self, request):
        """地址页通过post表单提交地址"""
        # 1.接收数据
        receiver = request.POST.get('receiver')
        addr = request.POST.get('addr')
        zip_code = request.POST.get('zip_code')
        phone = request.POST.get('phone')
        # 2.校验数据
        # 判断传入的数据是否为空，邮编可为空，所以不做校验
        if not all([receiver, addr, phone]):
            return render(request, 'user_center_site.html', {'errmsg': '数据不完整'})
        # 校验手机号
        if not re.match(r'^1[3|4|5|6|7|8][0-9]{9}$', phone):
            return render(request, 'user_center_site.html', {'errmsg': '手机格式不正确'})
        # 3.业务处理，地址添加
        # 如果用户已存在默认收货地址，添加的地址不作为默认收货地址，否则作为默认收货地址
        # 获取登录后的用户对象
        user = request.user
        # 根据用户对象，查询该对象的默认收货地址，如果存在收货地址则返回，不存在，则设置为NONE
        try:
            address = Address.objects.get(user=user, is_default=True)
        except Address.DoesNotExist:
            address = None

        # 根据上述查询的结果，决定新增的地址是否为默认收货地址
        if address:
            is_default = False
        else:
            is_default = True

        # 添加地址到地址表中
        Address.objects.create(user=user, receiver=receiver, addr=addr,
                               zip_code=zip_code, phone=phone, is_default=is_default)

        # 4.返回应答，刷新地址页面
        return redirect(reverse('user:address'))