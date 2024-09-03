import os
from pathlib import Path

from dotenv import load_dotenv


class Config:
    def __init__(self, env_file='.env'):
        base_dir = Path(__file__).resolve().parent.parent.parent
        # 读取 .env 文件
        env_file = base_dir / env_file
        load_dotenv(env_file)

    def get(self, key, default=None):
        # 优先从 .env 文件中获取变量，如果没有找到则从系统环境变量中获取
        return os.getenv(key, default)


config = Config()

