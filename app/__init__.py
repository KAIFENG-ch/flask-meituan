from flask import Flask
import conf


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(conf.config[config_name])
    conf.config[config_name].init_app(app)

    from utils import util as util_blueprint
    app.register_blueprint(util_blueprint)
    from .service.admin import admin
    app.register_blueprint(admin)
    from .service.delivery import delivery
    app.register_blueprint(delivery)
    from .service.shop import shop
    app.register_blueprint(shop)
    from .service.user import user
    app.register_blueprint(user)
    from log import log
    app.register_blueprint(log)

    return app
