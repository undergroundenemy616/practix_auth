from flask import Flask
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

from db.pg_db import init_db, db
from permissions import permissions
from accounts import accounts


def create_app(configuration='core.config.DevelopmentBaseConfig'):
    app = Flask(__name__)
    app.config.from_object(configuration)
    init_db(app)
    migrate = Migrate(app, db)
    import models
    JWTManager(app)
    app.register_blueprint(permissions, url_prefix='/api/v1/permissions')
    app.register_blueprint(accounts, url_prefix='/api/v1/accounts')
    return app


if __name__ == '__main__':
    app = create_app()
    app.run()
