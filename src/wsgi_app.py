from flask_jwt_extended import JWTManager
from gevent import monkey
from flasgger import Swagger

from db.pg_db import db
from db.redis_db import redis_db

monkey.patch_all()

from app import create_app

app = create_app()
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
