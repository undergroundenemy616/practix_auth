from http import HTTPStatus

from flasgger import Swagger
from flask import Flask, jsonify
from flask import session, request
from flask_jwt_extended import JWTManager
from flask_jwt_extended import get_jwt_identity, jwt_required, get_jwt, \
    verify_jwt_in_request
from flask_migrate import Migrate
from marshmallow import ValidationError

from db.pg_db import init_db, db
from db.redis_db import init_redis_db, redis_db

from models.accounts import User

import datetime

migrate = Migrate()


def validation_bad_request_handler(e):
    return jsonify({
        'status': 'error',
        'message': e.messages,
    }), HTTPStatus.BAD_REQUEST


def forbidden_handler(e):
    return jsonify({
            'status': 'error',
            'message': 'Ошибка доступа',
        }), HTTPStatus.FORBIDDEN


def create_app(configuration='core.config.DevelopmentBaseConfig'):
    from api.rbac import rbac
    from api.accounts import accounts
    app = Flask(__name__)
    app.config.from_object(configuration)
    init_db(app)
    init_redis_db(app)
    migrate.init_app(app, db)
    app.register_blueprint(rbac, url_prefix='/api/v1/rbac')
    app.register_blueprint(accounts, url_prefix='/api/v1/accounts')

    swagger = Swagger(app)
    jwt = JWTManager(app)
    app.register_error_handler(ValidationError, validation_bad_request_handler)
    app.register_error_handler(403, forbidden_handler)

    @app.before_request
    def rate_limit():
        user_id = 'anonymous'
        data = request.get_json() or {}
        login = data.get('login', None)
        if not login:
            login = get_jwt_identity()
        user = User.query.filter_by(login=login).first()
        if user:
            user_id = user.id

        pipe = redis_db.pipeline()
        now = datetime.datetime.now()
        key = f'{user_id}:{now.minute}'
        pipe.incr(key, 1)
        pipe.expire(key, 59)
        result = pipe.execute()
        request_number = result[0]
        if request_number > app.config['REQUEST_LIMIT_PER_MINUTE']:
            return jsonify({
                'status': 'error',
                'message': 'Слишком много запросов',
            }), HTTPStatus.TOO_MANY_REQUESTS

    @jwt.token_in_blocklist_loader
    def check_if_token_is_revoked(jwt_header, jwt_payload):
        jti = jwt_payload['jti']
        token_in_redis = redis_db.get(jti)
        return token_in_redis is not None

    @app.before_first_request
    def setup_db():
        db.create_all()

    @app.teardown_appcontext
    def close_db(sender, **extra):
        db.session.close()
        redis_db.close()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run()
