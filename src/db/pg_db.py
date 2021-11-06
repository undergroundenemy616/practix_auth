from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_db(app: Flask):
    username = app.config['POSTGRES_USER']
    password = app.config['POSTGRES_PASSWORD']
    host = app.config['POSTGRES_HOST']
    port = app.config['POSTGRES_PORT']
    database_name = app.config['POSTGRES_DB']
    app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{username}:{password}@{host}:{port}/{database_name}'
    db.init_app(app)
