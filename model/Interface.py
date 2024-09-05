"""
:keyword
    - Interface
    - Abstract Class
    - Abstract Method

:summary
    - Provide a common interface for a Model inference to be used in the EndPoint
    - This is an abstract class that will be inherited by the Model class
"""
import io
import tempfile
from abc import ABC, abstractmethod
from typing import List, Dict

import av
import cv2
import numpy as np
import torchaudio
from torchaudio.transforms import Resample


class BaseHandle(ABC):
    """
    Abstract class for the Model interface
    """

    @abstractmethod
    def initialize(self, **kwargs):
        """
        Initialize the model
        """
        pass

    @abstractmethod
    def preprocess(self, ctx):
        """
        Preprocess the input template_data
        """
        pass

    @abstractmethod
    def inference(self, ctx):
        """
        Perform inference on the template_data
        """
        pass

    @abstractmethod
    def postprocess(self, ctx):
        """
        Postprocess the output template_data
        """
        pass

    @abstractmethod
    def handle(self, ctx):
        """
        Handle the template_data
        """
        pass

    def load_wav_from_bytes(self, byte_data, target_sample_rate=16000):
        # 使用 io.BytesIO 将字节数据转换为类文件对象
        bytes_io = io.BytesIO(byte_data)
        # 使用 torchaudio 读取音频数据
        waveform, sample_rate = torchaudio.load(bytes_io)

        # 如果需要将采样率转换为目标采样率
        if sample_rate != target_sample_rate:
            resampler = Resample(orig_freq=sample_rate, new_freq=target_sample_rate)
            waveform = resampler(waveform)

        return waveform

    def load_wav_from_file(self, file_path, target_sample_rate=16000):
        # 使用 torchaudio 读取音频数据
        waveform, sample_rate = torchaudio.load(file_path)

        # 如果需要将采样率转换为目标采样率
        if sample_rate != target_sample_rate:
            resampler = Resample(orig_freq=sample_rate, new_freq=target_sample_rate)
            waveform = resampler(waveform)

        return waveform

    def decode_video_from_bytes(self, video_bytes: bytes, resize_factor=1, rotate=False, crop=(0, -1, 0, -1)):
        # 创建临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
            temp_file.write(video_bytes)
            temp_file_path = temp_file.name

        # 使用 OpenCV 读取视频
        video_stream = cv2.VideoCapture(temp_file_path)
        fps = video_stream.get(cv2.CAP_PROP_FPS)
        print('Reading video frames...')

        full_frames = []
        while True:
            still_reading, frame = video_stream.read()
            if not still_reading:
                video_stream.release()
                break
            if resize_factor > 1:
                frame = cv2.resize(frame, (frame.shape[1] // resize_factor, frame.shape[0] // resize_factor))

            if rotate:
                frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)

            y1, y2, x1, x2 = crop
            if x2 == -1: x2 = frame.shape[1]
            if y2 == -1: y2 = frame.shape[0]

            frame = frame[y1:y2, x1:x2]

            full_frames.append(frame)


        return full_frames, fps

    def decode_video_from_file(self, video_path, resize_factor=1, rotate=False, crop=(0, -1, 0, -1)):
        # 使用 OpenCV 读取视频
        video_stream = cv2.VideoCapture(video_path)
        fps = video_stream.get(cv2.CAP_PROP_FPS)
        print('Reading video frames...')

        full_frames = []
        while True:
            still_reading, frame = video_stream.read()
            if not still_reading:
                video_stream.release()
                break
            if resize_factor > 1:
                frame = cv2.resize(frame, (frame.shape[1] // resize_factor, frame.shape[0] // resize_factor))

            if rotate:
                frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)

            y1, y2, x1, x2 = crop
            if x2 == -1: x2 = frame.shape[1]
            if y2 == -1: y2 = frame.shape[0]

            frame = frame[y1:y2, x1:x2]

            full_frames.append(frame)

        return full_frames, fps
