from flask import Flask
from flask_redis import FlaskRedis

redis_db = FlaskRedis()


def init_redis_db(app: Flask):

    host = app.config['REDIS_HOST']
    port = app.config['REDIS_PORT']
    db = app.config['REDIS_DB']
    app.config['REDIS_URL'] = f"redis://{host}:{port}/{db}"

    redis_db.init_app(app)
