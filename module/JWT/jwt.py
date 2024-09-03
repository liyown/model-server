from datetime import datetime, timedelta
from typing import Union
from jose import jwt, JWTError
from pydantic import BaseModel

from module.config.env_config import config

# 你的密钥和算法配置
SECRET_KEY = config.get("login_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class TokenData(BaseModel):
    username: str


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    """
    创建JWT令牌
    :param data: 需要编码到JWT中的数据
    :param expires_delta: 令牌的有效期
    :return: JWT字符串
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str, credentials_exception):
    """
    验证JWT令牌的有效性
    :param token: 要验证的JWT令牌
    :param credentials_exception: 如果验证失败要抛出的异常
    :return: 解码后的数据
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    return token_data
