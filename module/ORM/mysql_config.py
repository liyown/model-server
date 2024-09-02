from playhouse.pool import PooledMySQLDatabase

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
