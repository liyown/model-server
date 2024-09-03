import datetime
import os.path
from io import BytesIO
from PIL import Image
from module.OSS.aliyun_oss import bucket, OSSBase


class OSSImageService(OSSBase):
    def __init__(self, prefix="image"):
        super().__init__(prefix)

    def upload_image_from_file(self, local_file_path, key):
        """上传图片，并根据月份分类添加前缀
        :param local_file_path: 本地图片路径
        :param key: 上传到 OSS 的图片名称
        :return: Image 对象，读取上传后的图片
        """
        full_key = self._get_full_key(key)
        self.bucket.put_object_from_file(full_key, local_file_path)
        return full_key

    def upload_image_from_image(self, key, image: Image):
        """上传图片，并根据月份分类添加前缀
        :param key: 上传到 OSS 的图片名称
        :param image: Image 对象
        :return: Image 对象，读取上传后的图片
        """
        full_key = self._get_full_key(key)
        # 将 Image 对象转为 BytesIO 对象
        image_bytes = BytesIO()
        image.save(image_bytes, format='png')
        image_bytes.seek(0)
        self.bucket.put_object(full_key, image_bytes)
        return full_key

    def download_image_to_image(self, key) -> Image:
        """
        下载并处理图片，统一返回 PNG 格式的 Image 对象
        :param key: 图片在 OSS 上的 key
        :return: Image 对象，读取处理后的图片
        """
        process = "image/format,png"
        # 下载图片到内存中
        result = self.bucket.get_object(key, process=process)
        image_data = result.read()

        # 通过 BytesIO 读取图片为 Image 对象
        image = Image.open(BytesIO(image_data))

        # 转换为255*255
        image = image.resize((255, 255))
        return image

    def download_image_to_file(self, key, local_file_path):
        """
        下载图片到本地文件
        :param key: 图片在 OSS 上的 key
        :param local_file_path: 本地文件路径
        """
        self.bucket.get_object_to_file(key, local_file_path)
        return local_file_path


if __name__ == '__main__':

    oss_image_service = OSSImageService()
    full_key = oss_image_service.upload_image_from_file("data/dog.png", "dog.png")
    print(full_key)
    image = oss_image_service.download_image_to_image(full_key)
    image.show()
