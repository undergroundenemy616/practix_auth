from http import HTTPStatus
from pprint import pprint
import click

from flask import current_app, redirect
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required, get_jwt, \
    verify_jwt_in_request
from flask_jwt_extended.exceptions import JWTExtendedException
from jwt import InvalidTokenError

from db.redis_db import redis_db
from models.accounts import User, History, SocialAccount
from schemas.accounts import UserSchemaDetailed, UserHistorySchema, UserLoginSchema
from utils import register_user, get_login_and_user_or_403, OAuthSignIn


from db.pg_db import db

accounts = Blueprint('accounts', __name__)


@accounts.cli.command("createsuperuser")
@click.argument("login")
@click.argument("password")
def create_user(login, password):
    result = register_user(login, password, superuser=True)
    pprint(result[0].json)


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
    user_try = UserLoginSchema().load(request.get_json())
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
        }), HTTPStatus.OK

    return jsonify({
        'status': 'error',
        'message': 'Неверная пара логин-пароль',
    }), HTTPStatus.FORBIDDEN


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
    login, user = get_login_and_user_or_403()
    if request.method == "GET":
        result = UserSchemaDetailed().dumps(user, ensure_ascii=False)
        return jsonify({
            'status': 'success',
            'message': f'Аккаунт {login}',
            'data': result
        }), HTTPStatus.OK

    new_user_info = UserSchemaDetailed().load(request.get_json(), partial=True)

    if new_login := new_user_info.get('login', None):
        if User.query.filter(User.login == new_login, User.id != user.id).first():
            return jsonify({
                'status': 'error',
                'message': 'Пользователь с таким login уже зарегистрирован',
            }), HTTPStatus.BAD_REQUEST

    if new_password := new_user_info.pop('password', None):
        user.set_password(new_password)

    User.query.filter_by(id=user.id).update(new_user_info)
    db.session.commit()

    return jsonify({
        'status': 'success',
        'message': f'Пользователь {login} успешно обновлен',
    }), HTTPStatus.OK


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
    login, user = get_login_and_user_or_403()
    paginated_user_history = History.query.filter_by(user_id=user.id).\
        paginate(page=request.args.get('page'),
                 per_page=request.args.get('count'))
    return jsonify({
            'status': 'success',
            'message': f'История действий {login}',
            'data': UserHistorySchema().dump(paginated_user_history.items, many=True)
        }), HTTPStatus.OK


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
    }), HTTPStatus.OK


@accounts.route('/unpin/<provider>')
@jwt_required()
def oauth_unpin(provider):
    login = get_jwt_identity()
    user = User.query.filter_by(login=login).first()
    if not user:
        return jsonify({
            'status': 'error',
            'message': f'Пользователь с таким jwt_identity не найден',
        }), HTTPStatus.UNAUTHORIZED
    social_account = SocialAccount.query.filter_by(user_id=user.id, social_name=provider).first()
    if not social_account:
        return jsonify({
            'status': 'error',
            'message': f'Прикрепленный аккаунт в соцсети {provider} не найден',
        }), HTTPStatus.NOT_FOUND
    db.session.remove(social_account)
    db.session.commit()
    return jsonify({
        'status': 'success',
        'message': f'Аккаунт соцсети {provider} успешно откреплен',
    }), HTTPStatus.OK


@accounts.route('/authorize/<provider>')
@jwt_required(optional=True)
def oauth_authorize(provider):
    if get_jwt_identity():
        redirect(current_app.config['HOST'])
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()


@accounts.route('/callback/<provider>')
@jwt_required(optional=True)
def oauth_callback(provider):
    if get_jwt_identity():
        redirect(current_app.config['HOST'])
    oauth = OAuthSignIn.get_provider(provider)
    social_id, email, username = oauth.callback()
    if not social_id:
        return jsonify({
            'status': 'error',
            'message': 'Ошибка авторизациии',
        }), HTTPStatus.UNAUTHORIZED
    user = SocialAccount.get_or_create_user(social_id=social_id,
                                            social_name=provider,
                                            username=username,
                                            email=email)
    access_token = create_access_token(identity=user.login)
    refresh_token = create_refresh_token(identity=user.login)
    return jsonify({
        'status': 'success',
        'message': f'Пользователь {user.login} авторизован',
        'access_token': access_token,
        'refresh_token': refresh_token
    }), HTTPStatus.OK


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
    }), HTTPStatus.OK


@accounts.after_request
def after_request_func(response):
    if request.path.endswith('register'):
        return response
    data = request.get_json() or {}
    login = data.get('login', None)
    if not login:
        try:
            verify_jwt_in_request()
        except InvalidTokenError:
            return response
        login = get_jwt_identity()
    user = User.query.filter_by(login=login).first()
    if user:
        user_device = request.headers.get("User-Device")
        if user_device:
            if user_device in ['smart', 'web', 'mobile']:
                history = UserHistorySchema().load({"user_id": str(user.id),
                                                    "user_agent": str(request.user_agent),
                                                    "info": f"{request.method} {request.path}",
                                                    "user_device_type": request.headers.get("User-Device")})
                db.session.add(history)
                db.session.commit()
    return response
