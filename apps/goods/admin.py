from django.contrib import admin
from .models import *
# Register your models here.

class BaseModelAdmin(admin.ModelAdmin):
    """新建一个类，继承自模型管理类，重写保存和删除方法"""
    def save_model(self, request, obj, form, change):
        """新增或者更新表中数据的时候调用"""
        # 调用父类的原方法
        super().save_model(request, obj, form, change)

        # 发出任务，让celery worker重写生成首页静态页面
        from celery_tasks.tasks import generate_static_index_html
        generate_static_index_html.delay()

    def delete_model(self, request, obj):
        """删除表中的数据时调用"""
        super().delete_model(request, obj)
        from celery_tasks.tasks import generate_static_index_html
        generate_static_index_html.delay()


# 对每个需要在首页生成数据的模型类，新建模型管理类，重写删除和保存的方法
# 但是代码一致，可以重用，所有模型管理类继承自新建的类。继承其重写的方法即可
class GoodsTypeAdmin(BaseModelAdmin):
    pass


class IndexGoodsBannerAdmin(BaseModelAdmin):
    pass


class IndexPromotionBannerAdmin(BaseModelAdmin):
    pass


class IndexTypeGoodsBannerAdmin(BaseModelAdmin):
    pass


admin.site.register(GoodsType, GoodsTypeAdmin)
admin.site.register(IndexTypeGoodsBanner, IndexTypeGoodsBannerAdmin)
admin.site.register(IndexGoodsBanner, IndexGoodsBannerAdmin)
admin.site.register(Goods)
admin.site.register(GoodsSKU)
admin.site.register(IndexPromotionBanner, IndexPromotionBannerAdmin)