from django.shortcuts import render, redirect, reverse
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


class DetailView(View):
    """详情页"""
    def get(self, request, goods_id):
        """根据商品id，即sku_id查找对应的商品详情"""
        # 存在用户自行输入的id信息查找信息，且商品不存在的情况
        try:
            sku = GoodsSKU.objects.get(id=goods_id)
        except GoodsSKU.DoesNotExist:
            # 商品不存在，返回首页
            return redirect(reverse('goods:index'))
        # 雪碧图展示的数据分类信息
        types = GoodsType.objects.all()
        # 根据查询出来的商品信息的类别，找出与其类别一样的新品的数据信息
        # 根据新品的创建时间进行正向排序，取前2个
        new_skus = GoodsSKU.objects.filter(type=sku.type).order_by('-create_time')[:2]
        # 获取同样SPU的商品不同的规格的类型数据
        same_spu_skus = GoodsSKU.objects.filter(goods=sku.goods).exclude(id=goods_id)
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

            # 添加用户的历史记录
            # 获取redis链接
            conn = get_redis_connection('default')
            # 生成用户历史记录的Key
            history_key = 'history_%d' % user.id
            # 存在同样商品的重复浏览，直接移除之前的浏览记录，然后从redis列表左侧重新添加新的记录
            # 移除列表中对应商品的浏览记录
            conn.lrem(history_key, 0, goods_id)
            # 把商品的信息插入到浏览记录的左侧
            conn.lpush(history_key, goods_id)
            # 限制历史浏览记录的长度为5
            conn.ltrim(history_key, 0, 4)

        # 组织模板上下文
        context = {
            'sku': sku,
            'types': types,
            'new_skus': new_skus,
            'cart_count': cart_count,
            'same_spu_skus': same_spu_skus
        }

        return render(request, 'detail.html', context)