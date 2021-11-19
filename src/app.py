from flask import Flask
from flask_migrate import Migrate

from db.pg_db import init_db, db
from db.redis_db import init_redis_db
from rbac import rbac
from accounts import accounts

migrate = Migrate()


def create_app(configuration='core.config.DevelopmentBaseConfig'):
    app = Flask(__name__)
    app.config.from_object(configuration)
    init_db(app)
    init_redis_db(app)
    migrate.init_app(app, db)
    import models
    app.register_blueprint(rbac, url_prefix='/api/v1/rbac')
    app.register_blueprint(accounts, url_prefix='/api/v1/accounts')

    return app


if __name__ == '__main__':
    app = create_app()
    app.run()
