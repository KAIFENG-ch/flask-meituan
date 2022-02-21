import jwt
from jwt import exceptions
import time


SECRET_KEY = "asgfddasdasdasgerher"


def create_token(name):
    """基于jwt创建token的函数"""
    global SECRET_KEY
    headers = {
        "alg": "HS256",
        "typ": "JWT"
    }
    exp = int(time.time() + 2000)
    payload = {
        "name": name,
        "exp": exp
    }
    token = jwt.encode(payload=payload, key=SECRET_KEY, algorithm='HS256', headers=headers).encode().decode('utf-8')
    # 返回生成的token
    return token


def validate_token(token):
    """校验token的函数，校验通过则返回解码信息"""
    global SECRET_KEY
    payload = None
    msg = None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms="HS256")
        # jwt有效、合法性校验
    except exceptions.ExpiredSignatureError:
        msg = 'token已失效'
    except jwt.DecodeError:
        msg = 'token认证失败'
    except jwt.InvalidTokenError:
        msg = '非法的token'
    return payload, msg
