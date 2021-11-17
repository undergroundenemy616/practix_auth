from flask import Flask
from flask_redis import FlaskRedis

redis_db = FlaskRedis()


def init_redis_db(app: Flask):

    host = app.config['REDIS_HOST']
    port = app.config['REDIS_PORT']
    app.config['REDIS_URL'] = f"redis://{host}:{port}/0"

    redis_db.init_app(app)
