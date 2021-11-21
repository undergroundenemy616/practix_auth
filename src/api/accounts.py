from pprint import pprint
import click

from flask import current_app
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required, get_jwt, \
    verify_jwt_in_request
from flask_jwt_extended.exceptions import JWTExtendedException
from marshmallow import ValidationError

from db.redis_db import redis_db
from models.accounts import User, History
from schemas.accounts import UserSchemaDetailed, UserHistorySchema, UserLoginSchema
from utils import register_user

from db.pg_db import db

accounts = Blueprint('accounts', __name__)


@accounts.cli.command("createsuperuser")
@click.argument("login")
@click.argument("password")
def create_user(login, password):
    result = register_user(login, password, superuser=True)
    pprint(result[0])


@accounts.route('/register', methods=['POST'])
def register():
    """register
    ---
    post:
      description: register_user
      summary: Register user
      parameters:
      - name: login
        in: path
        description: login
        schema:
          type: string
      - name: password
        in: path
        description: password
        schema:
          type: string
      - name: superuser
        in: path
        description: superuser
        schema:
          type: boolean
    responses:
      '201':
          description: Ok
      '403':
          description: Conflict
    tags:
    - account
    """
    return register_user(**request.get_json())


@accounts.route('/login', methods=['POST'])
def sign_in():
    """login
        ---
        post:
          description: register_user
          summary: Register user
          parameters:
          - name: login
            in: path
            description: login
            schema:
              type: string
          - name: password
            in: path
            description: password
            schema:
              type: string

          requestBody:
            content:
              application/json:
                schema: UserIn
        responses:
          '201':
            description: Ok
            schema:
              $ref: "#/definitions/TokensMsg"
          '403':
            description: Incorrect password or login name
            schema:
             $ref: "#/definitions/ApiResponse"
        tags:
          - account
        definitions:
          ApiResponse:
            type: "object"
            properties:
              message:
                type: "string"
              status:
                type: "string"
          TokensMsg:
           type: "object"
           properties:
             message:
               type: "string"
             status:
               type: "string"
             access_token:
               type: "string"
             refresh_token:
               type: "string"


        """
    try:
        user_try = UserLoginSchema().load(request.get_json())
    except ValidationError as e:
        return jsonify(e.messages), 400
    login_try = user_try['login']
    password_try = user_try['password']
    user = User.query.filter_by(login=login_try).first()
    if user and user.check_password(password_try):
        login = login_try
        access_token = create_access_token(identity=login)
        refresh_token = create_refresh_token(identity=login)

        return jsonify({
            'status': 'success',
            'message': f'Пользователь {login} авторизован',
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 200

    return jsonify({
        'status': 'error',
        'message': 'Неверная пара логин-пароль',
    }), 403


@accounts.route('/account', methods=['GET', 'POST'])
@jwt_required()
def account():
    """update password
        ---
        get:
          description: update_password
          summary: Update password
        post:
          description: update_password
          summary: Update Password
          parameters:
          - name: login
            in: path
            description: login
            schema:
              type: string
          - name: password
            in: path
            description: password
            schema:
              type: string

        responses:
          200:
            description: Ok
            schema:
             $ref: "#/definitions/ApiResponse"
          403:
            description: Forbidden error
            schema:
             $ref: "#/definitions/ApiResponse"
          400:
            description: User already exist
            schema:
             $ref: "#/definitions/ApiResponse"
        tags:
          - account
        definitions:
          ApiResponse:
            type: "object"
            properties:
              message:
                type: "string"
              status:
                type: "string"

        """
    login = get_jwt_identity()
    user = User.query.filter_by(login=login).first()

    if not user:
        return jsonify({
            'status': 'error',
            'message': 'Ошибка доступа',
        }), 403

    if request.method == "GET":
        result = UserSchemaDetailed().dumps(user, ensure_ascii=False)
        return jsonify({
            'status': 'success',
            'message': f'Аккаунт {login}',
            'data': result
        }), 200

    try:
        new_user_info = UserSchemaDetailed().load(request.get_json(), partial=True)
    except ValidationError as e:
        return jsonify({
                'status': 'error',
                'message': e.messages,
            }), 400

    if new_login := new_user_info.get('login', None):
        if User.query.filter(User.login == new_login, User.id != user.id).first():
            return jsonify({
                'status': 'error',
                'message': 'Пользователь с таким login уже зарегистрирован',
            }), 400

    if new_password := new_user_info.pop('password', None):
        user.set_password(new_password)

    User.query.filter_by(id=user.id).update(new_user_info)
    db.session.commit()

    return jsonify({
        'status': 'success',
        'message': f'Пользователь {login} успешно обновлен',
    }), 200


@accounts.route('/user-history', methods=['GET'])
@jwt_required()
def get_user_history():
    """get_user_history
       ---
       get:
         description: get_user_history
         summary: Get user history
         security:
           - jwt_access: []
       responses:
         200:
           description: Return login history
           schema:
             $ref: "#/definitions/UserHistory"
         403:
           description: Forbidden error
           schema:
             $ref: "#/definitions/ApiResponse"
       tags:
         - account
       definitions:
         ApiResponse:
           type: "object"
           properties:
             message:
              type: "string"
             status:
              type: "string"
         UserHistory:
            type: "object"
            properties:
              status:
                type: "string"
              message:
                type: "string"
              data:
                type: "object"
                properties:
                  user_id:
                    type: "string"
                    format: "uuid"
                  user_agent:
                     type: "string"
                  info:
                     type: "string"
                  date:
                    type: "string"
                    format: "date"
       """
    login = get_jwt_identity()
    user = User.query.filter_by(login=login).first()
    if not user:
        return jsonify({
            'status': 'error',
            'message': 'Ошибка доступа',
        }), 403
    paginated_user_history = History.query.filter_by(user_id=user.id).\
        paginate(page=request.args.get('page'),
                 per_page=request.args.get('count'))
    return jsonify({
            'status': 'success',
            'message': f'История действий {login}',
            'data': UserHistorySchema().dump(paginated_user_history.items, many=True)
        }), 200


@accounts.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """refresh password
       ---
       post:
         description: refresh_token
         summary: Refresh toke
         security:
           - jwt_access: []
       responses:
         '200':
            description: Return refresh token
            schema:
              $ref: "#/definitions/AccessTokenMsg"
       tags:
         - account
       definitions:
         AccessTokenMsg:
           type: "object"
           properties:
             message:
               type: "string"
             status:
               type: "string"
             access_token:
               type: "string"

       """
    identity = get_jwt_identity()
    jti = get_jwt()['jti']
    redis_db.set(jti, '', ex=current_app.config['JWT_ACCESS_TOKEN_EXPIRES'])
    access_token = create_access_token(identity=identity)

    return jsonify({
        'status': 'success',
        'message': 'Token успешно обновлен',
        'access_token': access_token,
    }), 200


@accounts.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """User logout point
       ---
       post:
         description: user_logout
         summary: User logaut
         security:
           - jwt_access: []
       responses:
         '200':
           description: Logout complete
           schema:
             $ref: "#/definitions/ApiResponse"
       tags:
         - account
       produces:
         - "application/json"
       definitions:
         ApiResponse:
           type: "object"
           properties:
             message:
              type: "string"
             status:
              type: "string"
       """
    login = get_jwt_identity()
    jti = get_jwt()['jti']
    redis_db.set(jti, '', ex=current_app.config['JWT_ACCESS_TOKEN_EXPIRES'])
    return jsonify({
        'status': 'success',
        'message': f'Сеанс пользователя {login} успешно завершен'
    }), 200


@accounts.after_request
def after_request_func(response):
    if request.path.endswith('register'):
        return response
    data = request.get_json() or {}
    login = data.get('login', None)
    if not login:
        try:
            verify_jwt_in_request()
        except JWTExtendedException:
            return response
        login = get_jwt_identity()
    user = User.query.filter_by(login=login).first()
    if user:
        history = UserHistorySchema().load({"user_id": str(user.id),
                                            "user_agent": str(request.user_agent),
                                            "info": f"{request.method} {request.path}"})
        db.session.add(history)
        db.session.commit()
    return response
