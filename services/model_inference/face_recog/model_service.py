"""
This module is used to load the model and perform inference on the input image.

从任务队列中获取任务，调用预处理函数，执行推理函数，调用后处理函数，将结果返回给任务结果缓存
"""
from queue import Queue
from threading import Thread

from model.face_recognition.face_recognition_handle import FaceRecognitionHandle

face_task_queue = Queue(100)

# 任务结果缓存
face_result_cache = {}


def get_result(task_id):
    return face_result_cache.get(task_id)


class FaceRecognitionService:
    def __init__(self, work_num=1):
        self.face_handle = FaceRecognitionHandle()
        self.ThreadPool = []
        for i in range(work_num):
            self.ThreadPool.append(Thread(target=self.run))

    def start(self):
        for thread in self.ThreadPool:
            thread.start()

    def run(self):
        while True:
            task = face_task_queue.get()
            task_id = task.get("task_id")
            ctx = task.get("ctx")
            self.face_handle.preprocess(ctx)
            self.face_handle.inference(ctx)
            result = self.face_handle.postprocess(ctx)
            face_result_cache[task_id] = result


