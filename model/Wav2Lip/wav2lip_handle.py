import os
import platform
import subprocess
from typing import Optional
import cv2
import numpy as np
from torch import Tensor
from tqdm import tqdm
from model.Interface import BaseHandle
import torch
from pydantic import BaseModel
from model.Wav2Lip import audio
from model.Wav2Lip.inference import load_model, get_smoothened_boxes
from model.Wav2Lip.face_detection.api import FaceAlignment, LandmarksType
from module.config.env_config import config
import logging
from utils.snowflake import Snowflake

from GFPGAN.gfpgan_handle import GFPGANHandle

logger = logging.getLogger(__name__)


class Wav2LipInputModel(BaseModel):
    """
    Wav2Lip模型配置
    """
    video_path: str
    audio_path: str
    improve_video: Optional[bool] = False
    # If True, then use only first video frame for inference
    resize_factor: Optional[float] = config.get("resize_factor", 1, dtype=float)
    rotate: Optional[bool] = config.get("rotate", False)


class Wav2LipHandle(BaseHandle):
    """
    人脸识别处理类
    """

    def __init__(self):
        self.model = None
        self.face_det_batch_size = config.get("face_det_batch_size", 1, dtype=int)
        self.box = (-1, -1, -1, -1)
        self.wav2lip_batch_size = config.get("wav2lip_batch_size", 128, dtype=int)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), config.get("temp_dir", "temp"))
        self.snowflake = Snowflake(2, 1)
        self.crop = [0, -1, 0, -1]
        self.static = False
        self.img_size = 96
        self.pad = [0, 10, 0, 0]
        self.nosmooth = False
        self.current_path = os.path.dirname(os.path.abspath(__file__))
        

        self.GFPGanHandle = GFPGANHandle()

    def initialize(self, **kwargs):
        """
        初始化人脸识别模型
        """
        self.model = load_model(os.path.join(self.current_path,"models/wav2lip.pth"), self.device)
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
        video, fps = self.decode_video_from_file(raw_data.video_path, raw_data.resize_factor, raw_data.rotate,
                                                 self.crop)
        logger.debug("Video data processed successfully")
        # 生成音频特征块
        mel_chunks = self.generate_audio_feature_chunks(mel, fps)

        if np.isnan(mel.reshape(-1)).sum() > 0:
            raise ValueError(
                'Mel contains nan! Using a TTS voice? Add a small epsilon noise to the wav file and try again')

        full_frames = video[:len(mel_chunks)]

        logger.debug("数据处理完成")

        gen_data = self.datagen(full_frames.copy(), mel_chunks)

        logger.debug("数据生成完成")

        return gen_data, len(mel_chunks), full_frames, fps, raw_data.audio_path, raw_data.improve_video

    def inference(self, input_data):
        """
        执行推理
        """
        temp_file_name = self.snowflake.generate_temp_dir()
        temp_file_full_path = f'{self.temp_dir}/{temp_file_name}.avi'

        output_file_full_path = f'{self.temp_dir}/{self.snowflake.generate_temp_dir()}.mp4'

        logger.debug("开始推理")
        logger.debug(self.device)
        for i, (img_batch, mel_batch, frames, coords) in enumerate(tqdm(input_data[0],
                                                                        total=int(
                                                                            np.ceil(float(input_data[
                                                                                              1])) / self.wav2lip_batch_size))):
            if i == 0:
                frame_h, frame_w = input_data[2][0].shape[:-1]
                if input_data[5]:
                    frame_h, frame_w = frame_h * 2, frame_w * 2
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

                # GFP-GAN 提高视频质量
                if input_data[5]:
                    f = self.GFPGanHandle.handle_frame(f)
                out.write(f)

        out.release()
        logger.debug("推理完成")

        command = 'ffmpeg -y -loglevel warning -i {} -i {} -strict -2 -q:v 1 {} '.format(input_data[4], temp_file_full_path,
                                                                      output_file_full_path)
        subprocess.call(command, shell=platform.system() != 'Windows')
        logger.debug("合成完成")
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

    def datagen(self, frames, mels):
        img_batch, mel_batch, frame_batch, coords_batch = [], [], [], []

        if self.box[0] == -1:
            if not self.static:
                face_det_results = self.face_detect(frames)  # BGR2RGB for CNN face detection
            else:
                # 结果为每个视频帧的人脸和坐标，为检测出来的实际人脸和坐标
                face_det_results = self.face_detect([frames[0]])
        else:
            print('Using the specified bounding box instead of face detection...')
            y1, y2, x1, x2 = self.box
            face_det_results = [[f[y1: y2, x1:x2], (y1, y2, x1, x2)] for f in frames]

        for i, m in enumerate(mels):
            idx = 0 if self.static else i % len(frames)
            frame_to_save = frames[idx].copy()
            face, coords = face_det_results[idx].copy()

            # 处理为模型输入的图片大小 96*96
            face = cv2.resize(face, (self.img_size, self.img_size))
            
            # 保存图片，此为resize后的图片
            img_batch.append(face)
            mel_batch.append(m)
            # 保存原始图片
            frame_batch.append(frame_to_save)

            # 保存人脸坐标
            coords_batch.append(coords)

            if len(img_batch) >= self.wav2lip_batch_size:
                img_batch, mel_batch = np.asarray(img_batch), np.asarray(mel_batch)

                img_masked = img_batch.copy()
                img_masked[:, self.img_size // 2:] = 0

                img_batch = np.concatenate((img_masked, img_batch), axis=3) / 255.
                mel_batch = np.reshape(mel_batch, [len(mel_batch), mel_batch.shape[1], mel_batch.shape[2], 1])

                yield img_batch, mel_batch, frame_batch, coords_batch
                img_batch, mel_batch, frame_batch, coords_batch = [], [], [], []

        if len(img_batch) > 0:
            img_batch, mel_batch = np.asarray(img_batch), np.asarray(mel_batch)

            img_masked = img_batch.copy()
            img_masked[:, self.img_size // 2:] = 0

            img_batch = np.concatenate((img_masked, img_batch), axis=3) / 255.
            mel_batch = np.reshape(mel_batch, [len(mel_batch), mel_batch.shape[1], mel_batch.shape[2], 1])

            yield img_batch, mel_batch, frame_batch, coords_batch

    def face_detect(self, images):
        detector = FaceAlignment(LandmarksType._2D, flip_input=False)

        batch_size = self.face_det_batch_size

        while 1:
            predictions = []
            try:
                for i in tqdm(range(0, len(images), batch_size)):
                    predictions.extend(detector.get_detections_for_batch(np.array(images[i:i + batch_size])))
            except RuntimeError:
                if batch_size == 1:
                    raise RuntimeError(
                        'Image too big to run face detection on GPU. Please use the --resize_factor argument')
                batch_size //= 2
                print('Recovering from OOM error; New batch size: {}'.format(batch_size))
                continue
            break

        results = []
        pady1, pady2, padx1, padx2 = self.pad
        for rect, image in zip(predictions, images):
            if rect is None:
                cv2.imwrite('temp/faulty_frame.jpg', image)  # check this frame where the face was not detected.
                raise ValueError('Face not detected! Ensure the video contains a face in all the frames.')

            y1 = max(0, rect[1] - pady1)
            y2 = min(image.shape[0], rect[3] + pady2)
            x1 = max(0, rect[0] - padx1)
            x2 = min(image.shape[1], rect[2] + padx2)

            results.append([x1, y1, x2, y2])

        boxes = np.array(results)
        if not self.nosmooth: boxes = get_smoothened_boxes(boxes, T=5)
        results = [[image[y1: y2, x1:x2], (y1, y2, x1, x2)] for image, (x1, y1, x2, y2) in zip(images, boxes)]

        del detector
        return results


# ------------------------------------------------------ 测试用例 ------------------------------------------------------

#
# wav2lipHandle = Wav2LipHandle()
# wav2lipHandle.initialize()
#
# raw_data = Wav2LipInputModel.parse_obj({
#     "face_path": "test/test.mp4",
#     "audio_path": "test/test_1.wav",
#     "resize_factor": 0.1,
# })
#
# result = wav2lipHandle.handle(raw_data)


def ttest_wav_byte_read():
    wav = audio.load_wav("test/test.wav", 16000)

    # 读取音频文件为字节
    with open("test/test.wav", "rb") as f:
        audio_bytes = f.read()

    wav2lipHandle = Wav2LipHandle()
    wav_2 = wav2lipHandle.load_wav_from_bytes(audio_bytes)

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

    wav2lipHandle = Wav2LipHandle()
    full_frames_2, fps_2 = wav2lipHandle.decode_video_from_bytes(video_bytes)

    # 检查视频数据是否相同
    assert len(full_frames) == len(full_frames_2)
    assert all(
        [torch.all(torch.eq(Tensor(frame), Tensor(video_frame))) for frame, video_frame in zip(full_frames, full_frames_2)])


def _test_mel_generate():
    wav_1 = audio.load_wav("test/test_1.wav", 16000)
    mel_1 = audio.melspectrogram(wav_1)

    wav2lipHandle = Wav2LipHandle()
    # 音频数据处理
    wav = wav2lipHandle.load_wav_from_file("test/test_1.wav")
    mel = audio.melspectrogram(wav)
    logger.debug("Audio data processed successfully")
    # 视频输入处理
    video, fps = wav2lipHandle.decode_video_from_file("test/test.mp4")
    logger.debug("Video data processed successfully")
    # 生成音频特征块
    mel_chunks = wav2lipHandle.generate_audio_feature_chunks(mel, fps)

    assert len(mel_chunks) == 10
    assert all([len(mel_chunk[0]) == 16 for mel_chunk in mel_chunks])
