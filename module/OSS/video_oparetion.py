import datetime
import os.path
import time
from io import BytesIO

import cv2
import numpy as np

from module.OSS.aliyun_oss import bucket, OSSBase


class OSSVideoService(OSSBase):
    def __init__(self, prefix="video"):
        super(OSSVideoService, self).__init__(prefix)

    def upload_video_from_file(self, file_path, object_name):
        """
        Upload video from file
        :param file_path: str, path to the file
        :param object_name: str, object name
        :return: str, object name
        """
        self.upload_file_from_file(file_path, object_name)
        return object_name

    def upload_video_from_bytes(self, object_name, file: BytesIO):
        """
        Upload video from bytes
        :param object_name: str, object name
        :param file: BytesIO, file
        :return: str, object name
        """
        full_key = self.upload_file_from_bytes(object_name, file)
        return full_key

    def download_video_to_bytes(self, object_name):
        """
        Download video to bytes
        :param object_name: str, object name
        :return: bytes
        """
        return self.bucket.get_object(object_name).read()


def bytes_to_video_frames():
    # 将字节数据转换为 NumPy 数组
    # np_arr = np.frombuffer(byte_data, np.uint8)

    # 使用 cv2.VideoCapture 创建视频流
    cap = cv2.VideoCapture(cv2.CAP_FFMPEG)

    # 打开内存中的视频数据流
    cap.open("data/test_v.mp4", cv2.CAP_FFMPEG)

    return cap


if __name__ == '__main__':
    oss_video_service = OSSVideoService()
    oss_video_service.upload_video_from_file("data/test_v.mp4", "test.mp4")
    print("done")



