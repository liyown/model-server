from queue import Queue
from threading import Thread
import logging
from typing import Dict

from model.face_recognition.face_recognition_handle import FaceRecognitionHandle, FaceRecognitionCTX
from module.ORM.model import ImageToVideoTaskModel, ImageToVideoResultModel
from module.retry.simple_retry import retry_with_timeout
from module.task_queue.persistence_queue import ImageToVideoTaskTaskQueue



logger = logging.getLogger(__name__)

# 任务队列
face_task_queue = ImageToVideoTaskTaskQueue(100)


def callback():
    print("任务失败")


class FaceRecognitionService:
    def __init__(self, work_num=1):
        self.face_handle = FaceRecognitionHandle()
        self.face_handle.initialize()
        self.ThreadPool = []
        for i in range(work_num):
            self.ThreadPool.append(Thread(target=self.run, daemon=True))
        logger.info(f"初始化人脸识别服务，工作线程数：{work_num}")

    def start(self):
        for thd in self.ThreadPool:
            thd.start()

        logger.info("人脸识别服务启动成功")

    @retry_with_timeout(max_attempts=3, delay=2, timeout_seconds=5, fail_callback=callback)
    def process_task(self, task: Dict):
        logger.info(f"开始处理任务 {task.get('task_id')}")
        task_id = task.get("task_id")
        ctx = task.get("image_url")
        result = self.face_handle.handle(FaceRecognitionCTX(image_path=ctx))
        logger.info(f"任务 {task_id} 处理完成")
        return result

    def run(self):
        while True:
            task = face_task_queue.get_task()
            try:
                self.process_task(task)
                face_task_queue.mark_task_as_done(task.get('task_id'), ImageToVideoResultModel.parse_obj({
                    "video_url": "http://example.com/video.mp4"
                }))
            except Exception as e:
                logger.error(f"任务 {task.get('task_id')} 处理失败: {e}")
                face_task_queue.mark_task_as_failed(task.get('task_id'))

    def stop(self):
        # 等待所有线程完成
        for thd in self.ThreadPool:
            thd.join()
        logger.info("所有线程已停止")


face_service = FaceRecognitionService(2)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    face_service = FaceRecognitionService(1)
    face_service.start()

    for i in range(10):
        face_task_queue.add_task(ImageToVideoTaskModel.parse_obj({
            "image_url": "data/dog.png",
            "audio_url": "http://example.com/audio.mp3",
            "status": 0
        }))

    # 守护线程
    for thread in face_service.ThreadPool:
        thread.join()


