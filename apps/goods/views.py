from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse
from .models import *
from django_redis import get_redis_connection
from django.views import View
from django.core.cache import cache
from django.core.paginator import Paginator


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


# /goods/商品id
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


# /list/种类id/页码?sort=排序方式
class ListView(View):
    """列表页"""
    def get(self, request, type_id, page):
        # 根据种类id，查找其对应的种类
        # 但是存在没有的种类的情况
        try:
            type = GoodsType.objects.get(id=type_id)
        except Exception as e:
            # 不存在的种类，直接跳转到首页
            return redirect(reverse('goods:index'))
        # 雪碧图展示的商品种类数据
        types = GoodsType.objects.all()
        # 根据种类类型，获取商品信息
        # 并且进行排序
        # 默认排序方式，sort = default
        # 价格排序，sort = price
        # 人气排序，按照销量排序，sort = hot
        # 排序是通过url参数传入的，需要通过request获取
        sort = request.GET.get('sort')
        if sort == 'price':
            skus = GoodsSKU.objects.filter(type=type).order_by('price')
        elif sort == 'hot':
            # - 表示降序，由高到低
            skus = GoodsSKU.objects.filter(type=type).order_by('-sales')
        else:
            # 未传入排序的方式，则以默认的方式排序
            sort = 'default'
            skus = GoodsSKU.objects.filter(type=type).order_by('-id')

        # 对获取到的数据进行分页,每页显示一个数据
        paginator = Paginator(skus, 1)
        # 获取第Page页的内容
        # 不存在的页码，返回至第一页
        try:
            page = int(page)
        except Exception as e:
            page = 1

        # 大于总页码的页码，也返回至第一页
        if page > paginator.num_pages:
            page = 1

        # 根据page页获取当前页的展示page对象
        skus_page = paginator.page(page)

        # 获取新品展示块的信息
        new_skus = GoodsSKU.objects.filter(type=type).order_by('-create_time')[:2]

        # 获取用户购物车中商品的数目
        user = request.user
        cart_count = 0
        if user.is_authenticated:
            # 用户已登录
            conn = get_redis_connection('default')
            cart_key = 'cart_%d' % user.id
            cart_count = conn.hlen(cart_key)
        # 进行页码的控制，页面上最多显示5个页码
        # 通过页码的索引范围，传入到模板，模板循环这个范围，组织翻页按钮
        # 1.总页数小于5页，页面上显示所有页码
        # 2.如果当前页是前3页，显示1-5页
        # 3.如果当前页是后3页，显示后5页
        # 4.其他情况，显示当前页、当前页的前2页、当前页的后2页
        # 后三种情况保证返回的页码列表数量为5即可
        num_pages = paginator.num_pages
        if num_pages < 5:
            # 显示全部页码
            # 所有页码的取值范围
            # 例如num_pages=3，那么就显示(1,4)列表中的翻页索引
            pages = range(1, num_pages+1)
        elif page <= 3:
            # 当前页为前3页
            # 例如num_pages=10，page=3, 那么就显示(1,6)列表中的翻页索引
            pages = range(1, 6)
        elif num_pages - page <=2:
            # 后三页，例如，8 ，9,10页
            # 例如num_pages=10，page=9, 那么就显示(6,11)列表中的翻页索引
            pages = range(num_pages-4, num_pages+1)
        else:
            # 例如num_pages=10，page=5, 那么就显示(3,8)列表中的翻页索引
            pages = range(page-2, page+3)

        # 组织模板上下文
        context = {
            'type': type,
            'types': types,
            'new_skus': new_skus,
            'cart_count': cart_count,
            'skus_page': skus_page,
            'sort': sort,
            'pages': pages
        }
        return render(request, 'list.html', context)