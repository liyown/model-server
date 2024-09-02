import queue
from module.ORM.mysql_config import db
from constants.ImageToVideoTaskConstants import ImageToVideoTaskStatus
from module.ORM.model import ImageToVideoTaskModel, ImageToVideoResultModel
from module.ORM.table_config import ImageToVideoTask, ImageToVideoResult
from peewee import DoesNotExist
import logging

from utils.snowflake import Snowflake

logger = logging.getLogger(__name__)


class ImageToVideoTaskTaskQueue:
    def __init__(self, max_size=100):
        # 初始化队列
        self.queue = queue.Queue(max_size)
        self.list = []

        self.Snowflake = Snowflake(1, 1)

        # 启动时加载未完成的任务到队列中
        self._load_pending_tasks()

    def _load_pending_tasks(self):
        """从数据库加载状态为排队中或处理中（status = 0 或 1）的任务."""
        pending_tasks = ImageToVideoTask.select().where(
            (ImageToVideoTask.status == ImageToVideoTaskStatus.PENDING.value) | (
                    ImageToVideoTask.status == ImageToVideoTaskStatus.PROCESSING.value)
        )
        logger.info(f"加载 {pending_tasks.count()} 个未完成任务到队列中")

        for task in pending_tasks:
            self.queue.put(task.__data__)

    def add_task(self, data: ImageToVideoTaskModel):
        """添加新任务到队列和数据库."""
        if self.queue.full():
            logger.info("任务队列已满")
            return None
        # 如果外面提供了id 则使用外面的id
        if data.task_id is None:
            task_id = self.Snowflake.generate()
            data.task_id = task_id

        # 创建新任务记录
        new_task = ImageToVideoTask.create(**data.model_dump())
        # 添加任务到队列
        self.queue.put(data.model_dump())
        logger.debug(f"添加任务 {new_task.task_id} 成功")
        return data.task_id

    def get_task(self):
        """从队列中获取一个任务."""
        task = self.queue.get()
        # 设置状态为处理中
        task_id = task.get('task_id')

        ImageToVideoTask.update(status=ImageToVideoTaskStatus.PROCESSING.value).where(
            ImageToVideoTask.task_id == task_id).execute()

        logger.debug(f"获取任务 {task_id} 成功")
        return task

    def mark_task_as_done(self, task_id: int, result: ImageToVideoResultModel):
        """标记任务为完成并更新数据库中的状态, 同时将结果保存到结果表."""
        if result.result_id is None:
            result.result_id = self.Snowflake.generate()
        # 创建新结果记录
        with db.atomic():
            ImageToVideoResult.create(**result.model_dump())
            # 更新任务状态
            ImageToVideoTask.update(status=ImageToVideoTaskStatus.COMPLETED.value, result_id=result.result_id).where(
                ImageToVideoTask.task_id == task_id).execute()
        logger.info(f"任务 {task_id} 处理完成")

    def mark_task_as_failed(self, task_id: int):
        """标记任务为失败并更新数据库中的状态."""
        ImageToVideoTask.update(status=ImageToVideoTaskStatus.FAILED.value).where(
            ImageToVideoTask.task_id == task_id).execute()
        logger.error(f"任务 {task_id} 处理失败")

    def get_result(self, task_id: int):
        """获取任务结果."""
        try:
            task = ImageToVideoTask.get(ImageToVideoTask.task_id == task_id)
        except DoesNotExist:
            logger.error(f"任务 {task_id} 不存在, 检查是否存在宕机情况")
            return None

        if task.status == ImageToVideoTaskStatus.COMPLETED.value:
            result = ImageToVideoResult.get(ImageToVideoResult.result_id == task.result_id)
            return result.__data__
        return None
