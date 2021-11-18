from flask import Flask
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

from db.pg_db import init_db, db
from db.redis_db import init_redis_db, redis_db
from permissions import permissions
from accounts import accounts


def create_app(configuration='core.config.DevelopmentBaseConfig'):
    app = Flask(__name__)
    app.config.from_object(configuration)
    init_db(app)
    init_redis_db(app)
    migrate = Migrate(app, db)
    import models
    app.register_blueprint(permissions, url_prefix='/api/v1/permissions')
    app.register_blueprint(accounts, url_prefix='/api/v1/accounts')
    jwt = JWTManager(app)


    @jwt.token_in_blocklist_loader
    def check_if_token_is_revoked(jwt_header, jwt_payload):
        jti = jwt_payload['jti']
        token_in_redis = redis_db.get(jti)
        return token_in_redis is not None

    return app


if __name__ == '__main__':
    app = create_app()
    app.run()
