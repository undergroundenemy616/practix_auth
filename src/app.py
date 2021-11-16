from flask import Flask
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

from core import config
from db.pg_db import init_db, db
from permissions import permissions
from accounts import accounts

app = Flask(__name__)
app.config.from_object(config.DevelopmentBaseConfig)
init_db(app)
migrate = Migrate(app, db)

jwt = JWTManager(app)
app.register_blueprint(permissions, url_prefix='/api/v1/permissions')
app.register_blueprint(accounts, url_prefix='/api/v1/accounts')

if __name__ == '__main__':
    app.run()
