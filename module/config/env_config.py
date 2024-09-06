import os
from pathlib import Path

from dotenv import load_dotenv


class Config:
    def __init__(self, env_file='.env'):
        base_dir = Path(__file__).resolve().parent.parent.parent
        # 读取 .env 文件
        env_file = base_dir / env_file
        load_dotenv(env_file)

    def get(self, key, default=None, dtype=str):
        # 优先从 .env 文件中获取变量，如果没有找到则从系统环境变量中获取
        if dtype == int:
            return int(os.getenv(key, default))
        if dtype == float:
            return float(os.getenv(key, default))
        return os.getenv(key, default)

    def get_logging_level(self):
        level = self.get("logging_level", "INFO")
        switcher = {
            "DEBUG": 10,
            "INFO": 20,
            "WARNING": 30,
            "ERROR": 40,
            "CRITICAL": 50
        }
        return switcher.get(level, 20)


config = Config()

