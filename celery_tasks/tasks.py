from celery import Celery
from django.conf import settings
from django.core.mail import send_mail

# worker端的环境初始化操作，任务发出者无需操作
# import os
# import django
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dailyfresh.settings')
# django.setup()

# 创建一个celery类的实例对象，名称自行设定,broker配置redis
app = Celery('celery_tasks.tasks', broker='redis://192.168.6.160:6379/8')

# 定义任务函数
# 并用celery对象装饰
@app.task
def send_register_active_email(to_email, username, token):
    """发送激活邮件"""
    # 组织邮件信息
    subject = '天天生鲜欢迎信息'
    # 邮件正文
    message = ''
    # 因为包含html的内容，需要通过html_message进行参数传递
    html_message = '<h1>%s, 欢迎您成为天天生鲜注册会员</h1>请点击下面链接激活您的账户<br/><a href="http://127.0.0.1:8000/user/active/%s">http://127.0.0.1:8000/user/active/%s</a>' % (
    username, token, token)
    # 发件人
    sender = settings.EMAIL_FROM
    # 收件人列表
    receiver = [to_email]
    send_mail(subject, message, sender, receiver, html_message=html_message)