import uuid


def create_unique_resource_token():
    """
    创建一个普通的唯一资源访问令牌
    :return: token
    """
    token = str(uuid.uuid4())
    return token

