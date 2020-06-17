from fdfs_client.client import Fdfs_client,get_tracker_conf

# 获取client.conf文件
tracker_path = get_tracker_conf('E:\python_project\Django\dailyfresh\dailyfresh\client.conf')
# 客户端对象
client = Fdfs_client(tracker_path)
# 上传文件
res = client.upload_by_filename('urls.py')
print(res)