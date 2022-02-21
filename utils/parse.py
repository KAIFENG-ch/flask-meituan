from flask import abort

from utils import JWT


def parseToken(token):
    if not token:
        abort(404)
    payload, msg = JWT.validate_token(token)
    if msg:
        return msg, False
    username = payload['name']
    return username, True
