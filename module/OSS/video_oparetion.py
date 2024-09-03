import datetime
import os.path
from io import BytesIO
from module.OSS.aliyun_oss import bucket, OSSBase


class OSSVideoService(OSSBase):
    def __init__(self, prefix="video"):
        super().__init__(prefix)




