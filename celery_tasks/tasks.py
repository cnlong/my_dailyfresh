from celery import Celery
from django.conf import settings
from django.core.mail import send_mail
from goods.models import GoodsType, IndexGoodsBanner,IndexPromotionBanner,IndexTypeGoodsBanner
from django_redis import get_redis_connection
from django.template import loader, RequestContext

# worker端的环境初始化操作，任务发出者无需操作
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dailyfresh.settings')
django.setup()

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


@app.task
def generate_static_index_html():
    # 获取商品的种类信息
    types = GoodsType.objects.all()
    # 获取首页轮播商品的信息
    goods_banners = IndexGoodsBanner.objects.all().order_by('index')
    # 获取首页促销的活动信息
    promotion_banners = IndexPromotionBanner.objects.all().order_by('index')
    # 获取首页分类商品的展示信息
    for type in types:
        # 获取type 种类下的首页分类商品的图片展示信息
        # 也就是首页主体商品展示块的大标题
        image_banners = IndexTypeGoodsBanner.objects.filter(type=type, display_type=1).order_by('index')
        # 获取type种类下的首页分类商品的文字展示信息
        # 也就是首页主体商品展示块的小标题
        title_banners = IndexTypeGoodsBanner.objects.filter(type=type, display_type=0).order_by('index')
        # 动态给type增加属性，分别保存首页分类商品的图片展示信息和文字展示信息
        # python是动态语言，能够动态添加属性
        type.image_banners = image_banners
        type.title_banners = title_banners
    # 构建上下文信息
    context = {'types': types,
               'goods_banners': goods_banners,
               'promotion_banners': promotion_banners}
    # 因为生产静态首页，用户未登录状态下访问的通用页面，无需购物车信息
    # 使用模板，获取静态页面的内容，而不是httpresponse对象
    # 1.加载模板文件
    temp = loader.get_template('static_index.html')
    # 2.模板渲染
    static_index_html = temp.render(context)
    # 3.将渲染后的模板生成一个静态页面文件
    save_path = os.path.join(settings.BASE_DIR, 'static/index1.html')
    with open(save_path, 'w') as f:
        f.write(static_index_html)