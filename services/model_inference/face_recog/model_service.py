from queue import Queue
from threading import Thread
import logging
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from model.face_recognition.face_recognition_handle import FaceRecognitionHandle
from module.retry.simple_retry import retry_with_timeout

logger = logging.getLogger(__name__)

# 任务队列
face_task_queue = Queue(100)
# 任务结果缓存
face_result_cache = {}
# 失败任务队列
face_failure_queue = Queue(100)


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
    def process_task(self, task):
        logger.info(f"开始处理任务 {task.get('task_id')}")
        task_id = task.get("task_id")
        ctx = task.get("ctx")
        self.face_handle.preprocess(ctx)
        self.face_handle.inference(ctx)
        result = self.face_handle.postprocess(ctx)
        face_result_cache[task_id] = result
        logger.info(f"任务 {task_id} 处理完成")

    def run(self):
        while True:
            task = face_task_queue.get()
            try:
                self.process_task(task)
            except Exception as e:
                logger.error(f"任务 {task.get('task_id')} 处理失败: {e}")
                face_failure_queue.put(task)

    def stop(self):
        # 设置停止事件
        self.stop_event.set()

        # 等待所有线程完成
        for thread in self.ThreadPool:
            thread.join()
        logger.info("所有线程已停止")


def get_result(task_id):
    return face_result_cache.get(task_id)

face_service = FaceRecognitionService(2)


if __name__ == "__main__":
    face_service = FaceRecognitionService(2)
    face_service.start()
    for i in range(10):
        face_task_queue.put({"task_id": i, "ctx": {"image_path": "data/dog.png"}})

    # 等待10s
    import time

    time.sleep(10)

    for i in range(10):
        print(get_result(i))
    print("任务处理完成")

    # 守护线程
    for thread in face_service.ThreadPool:
        thread.join()
