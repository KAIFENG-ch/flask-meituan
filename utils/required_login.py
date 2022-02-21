from flask_httpauth import HTTPTokenAuth

from utils import parse

auth = HTTPTokenAuth(scheme='JWT')


@auth.verify_token
def verify_token(token):
    try:
        username, ok = parse.parseToken(token)
        if not ok:
            return False
        return True
    except Exception as e:
        print("failed as %s" % e)
