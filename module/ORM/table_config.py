from peewee import Model, CharField, DateTimeField, IntegerField, TextField, MySQLDatabase, SQL, BigIntegerField, \
    AutoField
from datetime import datetime

from module.ORM.mysql_config import db


# 定义任务表模型
class ImageToVideoTask(Model):
    task_id = BigIntegerField(unique=True, primary_key=True)  # 任务ID
    # 可变字符串字段，最大长度为255
    image_key = CharField(max_length=255)  # 图片链接
    audio_key = CharField(max_length=255)  # 音频链接
    result_id = BigIntegerField(null=True)  # 生成视频结果ID
    created_at = DateTimeField(default=datetime.now)  # 创建时间
    updated_at = DateTimeField(default=datetime.now, constraints=[SQL('ON UPDATE CURRENT_TIMESTAMP')])  # 更新时间
    status = IntegerField(default=0)  # 状态 (0: 排队中, 1: 处理中, 2: 处理完成, 3: 处理失败)

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super().save(*args, **kwargs)

    class Meta:
        database = db  # 使用之前定义的数据库连接
        table_name = 'image_to_video_task'  # 表名


class ImageToVideoResult(Model):
    result_id = BigIntegerField(unique=True, primary_key=True)  # 结果ID
    video_key = CharField(max_length=255)  # 视频链接
    created_at = DateTimeField(default=datetime.now)  # 创建时间
    updated_at = DateTimeField(default=datetime.now, constraints=[SQL('ON UPDATE CURRENT_TIMESTAMP')])  # 更新时间

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super().save(*args, **kwargs)

    class Meta:
        database = db  # 使用之前定义的数据库连接
        table_name = 'image_to_video_result'  # 表名


class Authorizations(Model):
    id = AutoField()
    api_key = CharField(max_length=255)
    remark = TextField(null=True)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now, constraints=[SQL('ON UPDATE CURRENT_TIMESTAMP')])

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super().save(*args, **kwargs)

    class Meta:
        database = db
        table_name = 'authorizations'
        # 给api_key添加唯一索引
        indexes = (
            (('api_key'), True),
        )


# 检查表是否存在，不存在则创建
if not ImageToVideoTask.table_exists():
    db.create_tables([ImageToVideoTask])

if not ImageToVideoResult.table_exists():
    db.create_tables([ImageToVideoResult])

if not Authorizations.table_exists():
    db.create_tables([Authorizations])
