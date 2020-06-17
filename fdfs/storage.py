"""
编写自定义存储系统，使用外界的存储系统来存储文件图片等资源
"""
from django.core.files.storage import Storage
from fdfs_client.client import Fdfs_client,get_tracker_conf
from django.conf import settings


class FdfsStorage(Storage):
    """Fastdfs文件存储类"""
    def __init__(self, client_conf=None, base_url=None):
        """初始化，传入配置"""
        if client_conf is None:
            client_conf = settings.FDFS_CLIENT_CONF
        self.client_conf = client_conf
        if base_url is None:
            base_url = settings.FDFS_URL
        self.base_url = base_url
    def _open(self, name, mode='rb'):
        """打开文件使用"""
        pass

    def _save(self, name, content):
        """保存文件使用"""
        # name上传文件的名称
        # content包含上传文件内容的File对象

        # 1.获取client文件
        # 建议使用绝对路径
        tracker_path = get_tracker_conf(self.client_conf)
        # 2.客户端对象
        client = Fdfs_client(tracker_path)
        # 3.根据文件内容上传文件
        # 返回结果是一个字典
        res = client.upload_by_buffer(content.read())
        # dict
        # {
        #     'Group name': group_name,
        #     'Remote file_id': remote_file_id,
        #     'Status': 'Upload successed.',
        #     'Local file name': '',
        #     'Uploaded size': upload_size,
        #     'Storage IP': storage_ip
        # }
        # 根据返回结果，判断是否上传成功
        if res.get('Status') != 'Upload successed.':
            # 上传失败
            raise Exception('上传文件失败')

        # 上传成功，获取返回的文件ID
        filename = res.get('Remote file_id')
        # 注意返回结果是bytes类型，需要解码成字符串，Django才能接收处理
        return filename.decode()

    def exists(self, name):
        """Django判断文件名是否可用，因为保存至fdfs上，由fdfs自动生成为文件名，都为可用"""
        # 返回False表示可用
        return False

    def url(self, name):
        """返回访问文件的url路径"""
        # 这个参数name，就是上述保存之后返回的文件ID
        # 根据name，重构图片文件的url地址
        return self.base_url + name