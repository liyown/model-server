import time

from module.ORM.table_config import ImageToVideoTask, ImageToVideoResult
from utils.snowflake import Snowflake

Snowflake = Snowflake(1, 1)


def test_mysql_operation():
    task_id = Snowflake.generate()
    result_id = Snowflake.generate()

    # 测试代码
    task = ImageToVideoTask.create(
        task_id=task_id,
        result_id=result_id,
        image_url='http://example.com/image.jpg',
        audio_url='http://example.com/audio.mp3'
    )


def test_mysql_operation_update():
    task = ImageToVideoTask.get(ImageToVideoTask.task_id == 1280062908415479808)
    task.status = 4
    task.save()
