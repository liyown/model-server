import io
import os
import platform
import subprocess
from typing import Optional

import av
import cv2
import numpy as np
import torchaudio
from torch import Tensor
from torchaudio.transforms import Resample
from tqdm import tqdm

from model.Interface import BaseHandle
from torchvision.models import resnet18
from PIL import Image
import torchvision.transforms as transforms
import torch
from torchvision.models.resnet import ResNet18_Weights
from pydantic import BaseModel

from model.Wav2Lip import audio
from model.Wav2Lip.inference import load_model, datagen
from module.config.env_config import config
import logging

from utils.snowflake import Snowflake

logger = logging.getLogger(__name__)


class Wav2LipInputModel(BaseModel):
    """
    Wav2Lip模型配置
    """
    face_path: str
    audio_path: str
    # If True, then use only first video frame for inference
    static: Optional[bool] = config.get("static", False)
    resize_factor: Optional[float] = config.get("resize_factor", 1)
    nosmooth: Optional[bool] = config.get("nosmooth", False)
    crop: Optional[tuple] = config.get("crop", (0, -1, 0, -1))
    rotate: Optional[bool] = config.get("rotate", False)


class Wav2LipHandle(BaseHandle):
    """
    人脸识别处理类
    """

    def __init__(self):
        self.model = None
        self.face_det_batch_size = config.get("face_det_batch_size", 16)
        self.box = config.get("box", (-1, -1, -1, -1))
        self.wav2lip_batch_size = config.get("wav2lip_batch_size", 128)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.temp_dir = config.get("temp_dir", "temp")
        self.snowflake = Snowflake(2, 1)

    def initialize(self, **kwargs):
        """
        初始化人脸识别模型
        """
        self.model = load_model("model/Wav2Lip/checkpoints/wav2lip_gan.pth")
        logger.debug("Wav2Lip model loaded successfully")

    def preprocess(self, raw_data: Wav2LipInputModel):
        """
        预处理输入数据
        """
        # 音频数据处理
        wav = self.load_wav_from_file(raw_data.audio_path)
        mel = audio.melspectrogram(wav)
        logger.debug("Audio data processed successfully")
        # 视频输入处理
        video, fps = self.decode_video_from_file(raw_data.face_path, raw_data.resize_factor, raw_data.rotate,
                                                 raw_data.crop)
        logger.debug("Video data processed successfully")
        # 生成音频特征块
        mel_chunks = self.generate_audio_feature_chunks(mel, fps)

        if np.isnan(mel.reshape(-1)).sum() > 0:
            raise ValueError(
                'Mel contains nan! Using a TTS voice? Add a small epsilon noise to the wav file and try again')

        full_frames = video[:len(mel_chunks)]

        gen_data = datagen(full_frames.copy(), mel_chunks)

        return gen_data, len(mel_chunks), full_frames, fps, raw_data.audio_path

    def inference(self, input_data):
        """
        执行推理
        """
        temp_file_name = self.snowflake.generate_temp_dir()
        temp_file_full_path = f'{self.temp_dir}/{temp_file_name}.avi'

        output_file_full_path = f'{self.temp_dir}/{self.snowflake.generate_temp_dir()}'

        for i, (img_batch, mel_batch, frames, coords) in enumerate(tqdm(input_data[0],
                                                                        total=int(
                                                                            np.ceil(float(input_data[
                                                                                              1])) / self.wav2lip_batch_size))):
            if i == 0:
                frame_h, frame_w = input_data[2][0].shape[:-1]
                out = cv2.VideoWriter(temp_file_full_path,
                                      cv2.VideoWriter_fourcc(*'DIVX'), input_data[3], (frame_w, frame_h))

            img_batch = torch.FloatTensor(np.transpose(img_batch, (0, 3, 1, 2))).to(self.device)
            mel_batch = torch.FloatTensor(np.transpose(mel_batch, (0, 3, 1, 2))).to(self.device)

            with torch.no_grad():
                pred = self.model(mel_batch, img_batch)

            pred = pred.cpu().numpy().transpose(0, 2, 3, 1) * 255.

            for p, f, c in zip(pred, frames, coords):
                y1, y2, x1, x2 = c
                p = cv2.resize(p.astype(np.uint8), (x2 - x1, y2 - y1))

                f[y1:y2, x1:x2] = p
                out.write(f)

        out.release()

        command = 'ffmpeg -y -i {} -i {} -strict -2 -q:v 1 {}'.format(input_data[4], 'temp/result.avi',
                                                                      output_file_full_path)
        subprocess.call(command, shell=platform.system() != 'Windows')

        return output_file_full_path, temp_file_full_path

    def postprocess(self, output_data):
        """
        后处理输出数据,处理为可以返回的格式
        """
        # 读取视频文件为字节
        with open(output_data[0], "rb") as f:
            video_bytes = f.read()

        # 删除临时文件
        os.remove(output_data[0])
        os.remove(output_data[1])
        return video_bytes

    def handle(self, raw_data: Wav2LipInputModel):
        """
        pipeline
        """
        input_data = self.preprocess(raw_data)
        output_data = self.inference(input_data)
        return self.postprocess(output_data)

    def generate_audio_feature_chunks(self, mel, fps):
        """
        生成音频特征块
        """
        # 生成音频特征块
        mel_idx_multiplier = 80. / fps
        i = 0
        mel_step_size = 16
        mel_chunks = []
        # 为了保证 mel_step_size 个时间步长的音频特征对应的梅尔频谱图是连续的，需要对音频特征进行分块处理
        while 1:
            start_idx = int(i * mel_idx_multiplier)
            if start_idx + mel_step_size > len(mel[0]):
                mel_chunks.append(mel[:, len(mel[0]) - mel_step_size:])
                break
            mel_chunks.append(mel[:, start_idx: start_idx + mel_step_size])
            i += 1
        return mel_chunks


# ------------------------------------------------------ 测试用例 ------------------------------------------------------

def ttest_wav_byte_read():
    wav = audio.load_wav("test/test.wav", 16000)

    # 读取音频文件为字节
    with open("test/test.wav", "rb") as f:
        audio_bytes = f.read()

    faceRecognitionHandle = FaceRecognitionHandle()
    wav_2, _ = faceRecognitionHandle.load_wav_from_bytes(audio_bytes)

    # 检查音频数据是否相同
    assert torch.all(torch.eq(Tensor(wav), wav_2))

    print(Tensor(wav).mean())
    print(wav_2.mean())


def ttest_video_byte_read():
    video_stream = cv2.VideoCapture("test/test.mp4")
    fps = video_stream.get(cv2.CAP_PROP_FPS)

    print('Reading video frames...')

    full_frames = []
    while 1:
        still_reading, frame = video_stream.read()
        if not still_reading:
            video_stream.release()
            break
        y1, y2, x1, x2 = (0, -1, 0, -1)
        if x2 == -1: x2 = frame.shape[1]
        if y2 == -1: y2 = frame.shape[0]

        frame = frame[y1:y2, x1:x2]

        full_frames.append(frame)

    # 读取视频文件为字节
    with open("test/test.mp4", "rb") as f:
        video_bytes = f.read()

    faceRecognitionHandle = FaceRecognitionHandle()
    video = faceRecognitionHandle.decode_video_from_bytes(video_bytes)

    # 检查视频数据是否相同
    assert len(full_frames) == len(video)
    assert all(
        [torch.all(torch.eq(Tensor(frame), Tensor(video_frame))) for frame, video_frame in zip(full_frames, video)])
