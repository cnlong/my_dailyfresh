# 定义索引类
from haystack import indexes
# 导入需要建立索引的模型类
from .models import GoodsSKU


# 指定对于某个类的某些数据建立索引
# 索引类的名称格式：模型类名+Index
class GoodsSKUIndex(indexes.SearchIndex, indexes.Indexable):
    # use_template=True指定数据表中的哪些字段建立索引文件，需要新建一个专门的文件来存放这些字段
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        # 返回建立索引的模型类
        return GoodsSKU

    # 建立索引数据
    def index_queryset(self, using=None):
        return self.get_model().objects.all()