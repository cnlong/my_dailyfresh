from django.shortcuts import render
from django.http import HttpResponse
from .models import *
from django_redis import get_redis_connection
from django.views import View
from django.core.cache import cache


# Create your views here.
class IndexView(View):
    """首页"""
    def get(self, request):
        # 用户访问首页的时候，判断缓存中是否有数据，有即从缓存中获取
        context = cache.get('index_page')
        if context is None:
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
            # 缓存查询到的公用数据，缓存时间为1小时
            cache.set('index_page', context, 3600)
        # 获取用户购物车中的商品的数目
        user = request.user
        cart_count = 0
        # 用户已验证登录,才能获取其对应的购物车数目
        if user.is_authenticated:
            # default是settings中配置的redis连接的相关信息
            conn = get_redis_connection('default')
            cart_key = 'cart_%d' % user.id
            # 从redis中获取用户购物车的商品类型条目
            # hlen计算hash对应的值的数据数量
            cart_count = conn.hlen(cart_key)
        # 更新context上下文
        context.update(cart_count=cart_count)
        return render(request, 'index.html', context)
