import requests
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from core import config
from db.pg_db import init_db

app = Flask(__name__)


@app.route('/hello-world')
def hello_world():
    return 'Hello, World!'


def main():
    app.config.from_object(config.DevelopmentBaseConfig)
    init_db(app)
    app.run()


if __name__ == '__main__':
    main()
