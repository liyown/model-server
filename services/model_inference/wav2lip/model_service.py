import os.path
from threading import Thread
import logging
from typing import Dict

import requests

from model.Wav2Lip.wav2lip_handle import Wav2LipHandle, Wav2LipInputModel
from module.ORM.model import ImageToVideoTaskModel, ImageToVideoResultModel, VideoAndAudioToVideoTaskModel, \
    VideoAndAudioToVideoResultModel
from module.OSS.Audio_oparetion import OSSAudioService
from module.OSS.video_oparetion import OSSVideoService
from module.config.env_config import config
from module.retry.simple_retry import retry_with_timeout
from module.task_queue.persistence_queue import ImageToVideoTaskTaskQueue, VideoAndAudioToVideoTaskTaskQueue

logger = logging.getLogger(__name__)

# 任务队列
video_with_audio_task_queue = VideoAndAudioToVideoTaskTaskQueue(
    config.get("video_with_audio_task_service_queue_size", 100, int))


def callback():
    print("任务失败")


class VideoAndAudioToVideoService:
    def __init__(self, work_num=1):
        self.face_handle = Wav2LipHandle()
        self.face_handle.initialize()
        self.ThreadPool = []
        self.OSSAudioService = OSSAudioService()
        self.OSSVideoService = OSSVideoService()
        self.temp_path = "model/Wav2Lip/temp"
        for i in range(work_num):
            self.ThreadPool.append(Thread(target=self.run, daemon=True))
        logger.info(f"初始化wav2lip服务成功, 线程数: {work_num}")

    def start(self):
        for thd in self.ThreadPool:
            thd.start()

        logger.info("wav2lip服务已启动")

    @retry_with_timeout(max_attempts=3, delay=5, timeout_seconds=300, fail_callback=callback)
    def process_task(self, task: Dict):
        logger.debug(f"开始处理任务 {task.get('task_id')}")
        task_id = task.get("task_id")
        video_key = task.get("video_key")
        audio_key = task.get("audio_key")
        improve_video = task.get("improve_video")

        # 下载视频到临时文件
        # todo 支持更多格式文件
        video_file_path = os.path.join(self.temp_path, f"{task_id}.mp4")
        self.OSSVideoService.download_file_to_file(video_key, video_file_path)
        logger.debug(f"任务 {task_id} 视频下载完成, 地址: {video_file_path}")
        # 下载音频到临时文件
        # todo 支持更多格式文件
        audio_file_path = os.path.join(self.temp_path, f"{task_id}.wav")
        self.OSSAudioService.download_audio_to_file(audio_key, audio_file_path)
        logger.debug(f"任务 {task_id} 音频下载完成, 地址: {audio_file_path}")
        result = self.face_handle.handle(Wav2LipInputModel.parse_obj({
            "video_path": video_file_path,
            "audio_path": audio_file_path,
            "improve_video":improve_video
        }))
        # 上传到 OSS
        result_object_key = str(task_id) + ".mp4"
        full_key = self.OSSVideoService.upload_video_from_bytes(result_object_key, result)
        logger.debug(f"任务 {task_id} 结果上传完成, 地址: {result_object_key}")
        # 删除临时文件
        os.remove(video_file_path)
        os.remove(audio_file_path)
        logger.debug(f"任务 {task_id} 处理完成")
        return full_key

    def run(self):
        while True:
            task = video_with_audio_task_queue.get_task()
            try:
                full_key = self.process_task(task)
                video_with_audio_task_queue.mark_task_as_done(task.get('task_id'),
                                                              VideoAndAudioToVideoResultModel.parse_obj({
                                                                  "video_key": full_key
                                                              }))
                # 调用回调
                if task.get("callback_url"):
                    requests.post(task.get("callback_url"),
                                  json={"code": 200, "msg": "success", "data": {"video_key": full_key}})

            except Exception as e:
                logger.error(f"任务 {task.get('task_id')} 处理失败: {e}")
                video_with_audio_task_queue.mark_task_as_failed(task.get('task_id'), str(e))
                if task.get("callback_url"):
                    requests.post(task.get("callback_url"),
                                  json={"code": 500, "msg": "failed", "data": {"reason": str(e)}})

    def stop(self):
        # 等待所有线程完成
        logger.info("所有线程已停止")


video_with_audio_task_service = VideoAndAudioToVideoService(
    config.get("video_with_audio_task_service_thread_num", 1, int))
