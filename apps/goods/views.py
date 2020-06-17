from django.shortcuts import render
from django.http import HttpResponse
from .models import *
from django_redis import get_redis_connection

# Create your views here.
def index(request):
    # 获取商品的种类信息
    types = GoodsType.objects.all()
    # 获取首页轮播商品的信息
    goods_banners = IndexGoodsBanner.objects.all().order_by('index')
    for banner in goods_banners:
        print(banner.image.url)
    # 获取首页促销的活动信息
    promotion_banners = IndexPromotionBanner.objects.all().order_by('index')
    # 获取首页分类商品的展示信息
    for type in types:
        # 获取type 种类下的首页分类商品的图片展示信息
        # 也就是首页主体商品展示块的大标题
        image_banners = IndexTypeGoodsBanner.objects.filter(type=type, display_type=1).order_by('index')
        # 获取type种类下的首页分类商品的文字膳食信息
        # 也就是首页主体商品展示块的小标题
        title_banners = IndexTypeGoodsBanner.objects.filter(type=type, display_type=0).order_by('index')
        # 动态给type增加属性，分别保存首页分类商品的图片展示信息和文字展示信息
        type.image_bannsers = image_banners
        type.title_bannsers = title_banners

    # 构建上下文信息
    context = {'types': types,
               'goods_banners': goods_banners,
               'promotion_banners': promotion_banners}

    # 获取用户购物车中的商品的数目
    user = request.user
    cart_count = 0
    # 如果用户已验证登录
    if user.is_authenticated:
        # default是settings中配置的redis连接的相关信息
        conn = get_redis_connection('default')
        cart_key = 'cart_%d' % user.id
        # 从redis中获取用户购物车的数量
        cart_count = conn.hlen(cart_key)

    # 更新context上下文
    context.update(cart_count=cart_count)
    return render(request, 'index.html', context)