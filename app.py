import pymysql
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

import articles
import users
from config import Config
from database import db
from exc import InvalidUsage

pymysql.install_as_MySQLdb()


def create_app(config_object=Config):
    app = Flask(__name__.split('.')[0])
    app.url_map.strict_slashes = False
    app.config.from_object(config_object)
    register_extensions(app)
    register_blueprints(app)
    register_errorhandlers(app)
    return app


def register_extensions(app):
    db.init_app(app)
    JWTManager().init_app(app)
    Migrate().init_app(app, db)


def register_blueprints(app):
    app.register_blueprint(users.views.blueprint)
    app.register_blueprint(articles.views.blueprint)


def register_errorhandlers(app):
    def errorhandler(error):
        response = error.to_json()
        response.status_code = error.status_code
        return response

    app.errorhandler(InvalidUsage)(errorhandler)


app = create_app()
with app.app_context():
    # db.drop_all()
    db.create_all()
if __name__ == '__main__':
    app.run()
