from functools import wraps
import logging
from playhouse.pool import PooledMySQLDatabase
from pymysql import OperationalError

# 创建 MySQL 数据库连接
db = PooledMySQLDatabase(
    'AI_digital_human',  # 数据库名
    max_connections=8,
    stale_timeout=300,
    user='root',  # 用户名
    password='UHz~7Gi5(!g2',  # 密码
    host='120.79.60.251',  # 数据库地址
    port=3306  # 端口号，默认是 3306
)

logger = logging.getLogger(__name__)

# 创建一个装饰器，用于处理数据库连接
def with_db_connection(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            # 连接数据库
            if db.is_closed():
                db.connect()
                logger.info("Database connection opened")
            # 执行被装饰的函数
            result = func(*args, **kwargs)
        except OperationalError as e:
            print(f"Database operation failed: {e}")
            result = None
        finally:
            # 关闭数据库连接（如果没有在使用）
            if not db.is_closed():
                db.close()
                logger.info("Database connection closed")
        return result
    return wrapper