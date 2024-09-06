import datetime
import os.path
from io import BytesIO
from module.OSS.aliyun_oss import OSSBase


class OSSAudioService(OSSBase):
    def __init__(self, prefix="audio"):
        super().__init__(prefix)

    def upload_audio_from_file(self, local_file_path, key):
        """上传音频
        :param local_file_path: 本地音频路径
        :param key: 上传到 OSS 的音频名称
        """
        full_key = self._get_full_key(key)
        self.bucket.put_object_from_file(full_key, local_file_path)
        return full_key

    def upload_audio_from_audio(self, key, audio: BytesIO):
        """上传音频
        :param key: 上传到 OSS 的音频名称
        :param audio: BytesIO 对象
        """
        full_key = self._get_full_key(key)
        self.bucket.put_object(full_key, audio)
        return full_key

    def download_audio_to_file(self, key, local_file_path):
        """下载音频
        :param key: 音频在 OSS 上的 key
        :param local_file_path: 本地文件路径
        """
        self.bucket.get_object_to_file(key, local_file_path)
        return local_file_path

    def download_audio_to_bytes(self, key) -> bytes:
        """下载音频
        :param key: 音频在 OSS 上的 key
        """
        result = self.bucket.get_object(key)
        audio_data = result.read()
        return audio_data



if __name__ == '__main__':
    oss_audio_service = OSSAudioService()
    key = oss_audio_service.upload_audio_from_file("data/test_1.wav", "test_1.wav")
    print(key)