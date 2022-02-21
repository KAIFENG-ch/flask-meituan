import yaml
import os
import pymysql
import redis

filePath = os.path.dirname(__file__)
fileNamePath = os.path.split(os.path.realpath(__file__))[0]
yamlPath = os.path.join(fileNamePath, 'config.yaml')
f = open(yamlPath, 'r', encoding='utf-8')
cont = f.read()
x = yaml.load(cont, Loader=yaml.FullLoader)

db = pymysql.connect(
    host=x['DB']['host'],
    user=x['DB']['username'],
    password=x['DB']['password'],
    port=x['DB']['port'],
    database=x['DB']['database']
)

pool = redis.ConnectionPool(
    host=x['Redis']['host'],
    port=x['Redis']['port'],
    decode_responses=True
)

r = redis.Redis(connection_pool=pool)


def commit():
    db.commit()


def e():
    db.rollback()


class Config(object):
    SECRET_KEY = os.urandom(24)

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    DEBUG = False


class ProductionConfig(Config):
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'test': TestingConfig,
    'product': ProductionConfig
}
