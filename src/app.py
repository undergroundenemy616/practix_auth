import requests
from flask import Flask

from core import config
from db.pg_db import init_db

app = Flask(__name__)


@app.route('/hello-world')
def hello_world():
    requests.get('http://slow_application_host/slow-operation§')
    return 'Hello, World!'


app.config.from_object(config)


def main():
    init_db(app)
    app.run()


if __name__ == '__main__':
    main()
