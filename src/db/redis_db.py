import redis
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from app import app

db = SQLAlchemy()

host = app.config['REDIS_HOST']
port = app.config['REDIS_PORT']

redis_db = redis.Redis(host=host, port=port, db=0)
