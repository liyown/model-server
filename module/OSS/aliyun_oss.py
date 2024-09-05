import datetime
import logging
import os
from io import BytesIO
import oss2
from module.config.env_config import config

access_key_id = config.get("oss_access_key_id", " ")
access_key_secret = config.get("oss_access_key_secret", " ")
bucket_name = config.get("bucket_name", " ")
endpoint = config.get("endpoint", " ")

# 确认上面的参数都填写正确了
for param in (access_key_id, access_key_secret, bucket_name, endpoint):
    assert param.strip(), "请填写正确的参数"

# 创建Bucket对象，所有Object相关的接口都可以通过Bucket对象来进行
bucket = oss2.Bucket(oss2.Auth(access_key_id, access_key_secret), endpoint, bucket_name)
logger = logging.getLogger(__name__)


class OSSBase:
    def __init__(self, prefix):
        self.bucket = bucket
        self.prefix = prefix

    def _get_full_key(self, key):
        """生成带前缀和月份的完整 key"""
        current_month = datetime.datetime.now().strftime('%Y/%m/')
        # OSS 的 key 使用 / 分隔，所以需要替换掉 Windows 的路径分隔符
        full_key = os.path.join(self.prefix, current_month, key).replace(os.sep, '/')
        logger.debug(f"生成完整 key: {full_key}")
        return full_key

    def upload_file_from_file(self, local_file_path, key):
        """上传文件，并根据月份分类添加前缀
        :param local_file_path: 本地文件路径
        :param key: 上传到 OSS 的文件名称
        """
        full_key = self._get_full_key(key)
        self.bucket.put_object_from_file(full_key, local_file_path)
        return full_key

    def upload_file_from_bytes(self, key, file: BytesIO):
        """上传文件，并根据月份分类添加前缀
        :param key: 上传到 OSS 的文件名称
        :param file: BytesIO 对象
        """
        full_key = self._get_full_key(key)
        self.bucket.put_object(full_key, file)
        return full_key

    def download_file_to_file(self, key, local_file_path):
        """下载文件
        :param key: 文件在 OSS 上的 key
        :param local_file_path: 本地文件路径
        """
        self.bucket.get_object_to_file(key, local_file_path)
        return local_file_path

    def download_file_to_bytes(self, key):
        """下载文件
        :param key: 文件在 OSS 上的 key
        """
        result = self.bucket.get_object(key)
        return result.read()


if __name__ == '__main__':
    # 上传文件
    result = bucket.put_object_from_file("template_data/test_1.jpg", "template_data/test_1.jpg")

    # 下载文件
    bucket.get_object_to_file("template_data/test_1.jpg", "test_1.jpg")
    print("下载成功")