from flasgger import Swagger
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

from db.pg_db import init_db, db
from db.redis_db import init_redis_db, redis_db
from api.rbac import rbac
from api.accounts import accounts

migrate = Migrate()


def create_app(configuration='core.config.DevelopmentBaseConfig'):
    app = Flask(__name__)
    app.config.from_object(configuration)
    init_db(app)
    init_redis_db(app)
    migrate.init_app(app, db)
    app.register_blueprint(rbac, url_prefix='/api/v1/rbac')
    app.register_blueprint(accounts, url_prefix='/api/v1/accounts')

    swagger = Swagger(app)
    jwt = JWTManager(app)

    @jwt.token_in_blocklist_loader
    def check_if_token_is_revoked(jwt_header, jwt_payload):
        jti = jwt_payload['jti']
        token_in_redis = redis_db.get(jti)
        return token_in_redis is not None

    @app.before_first_request
    def setup_db():
        db.create_all()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run()
