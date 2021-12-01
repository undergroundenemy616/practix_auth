import functools
from http import HTTPStatus

from flask import jsonify, url_for, redirect, request, current_app
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity
from marshmallow import ValidationError
from werkzeug.exceptions import abort

from db.pg_db import db
from models.accounts import User
from models.rbac import Role
from schemas.accounts import UserLoginSchema

from abc import abstractmethod
from rauth import OAuth2Service
import json

def register_user(login, password, superuser=False):
    try:
        UserLoginSchema().load({'login': login, 'password': password})
    except ValidationError as e:
        return jsonify({'status': 'error',
                        'message': e.messages}), HTTPStatus.BAD_REQUEST
    if User.query.filter_by(login=login).first():
        return jsonify({
            'status': 'error',
            'message': 'Пользователь с таким login уже зарегистрирован'}), HTTPStatus.BAD_REQUEST
    if superuser:
        role_id = Role.query.filter_by(name='Admin').first().id
    else:
        role_id = Role.query.filter_by(name='BaseUser').first().id
    user = User(login=login, role_id=role_id)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    access_token = create_access_token(identity=login)
    refresh_token = create_refresh_token(identity=login)
    return jsonify({
        'status': 'success',
        'message': f'Пользователь {login} успешно зарегистрирован',
        'access_token': access_token,
        'refresh_token': refresh_token
    }), HTTPStatus.CREATED


def check_role(required_role: str):
    def check_admin_inner(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            login = get_jwt_identity()
            if not User.check_permission(login=login, required_role=required_role):
                abort(403)
            return f(*args, **kwargs)

        return wrapper

    return check_admin_inner


def get_login_and_user_or_403():
    login = get_jwt_identity()
    user = User.query.filter_by(login=login).first()
    if not user:
        abort(403)
    return login, user


class OAuthSignIn(object):
    providers = None

    def __init__(self, provider_name):
        self.provider_name = provider_name
        credentials = current_app.config['OAUTH_CREDENTIALS'][provider_name]
        self.consumer_id = credentials['id']
        self.consumer_secret = credentials['secret']

    @abstractmethod
    def authorize(self):
        pass

    @abstractmethod
    def callback(self):
        pass

    def get_callback_url(self):
        return url_for('accounts.oauth_callback',
                       provider=self.provider_name,
                       _external=True)

    @classmethod
    def get_provider(cls, provider_name):
        if cls.providers is None:
            cls.providers = {}
            for provider_class in cls.__subclasses__():
                provider = provider_class()
                cls.providers[provider.provider_name] = provider
        return cls.providers[provider_name]


class YandexSignIn(OAuthSignIn):
    def __init__(self):
        super(YandexSignIn, self).__init__('yandex')
        self.service = OAuth2Service(
            name='yandex',
            client_id=self.consumer_id,
            client_secret=self.consumer_secret,
            authorize_url='https://oauth.yandex.ru/authorize',
            access_token_url='https://oauth.yandex.ru/token',
            base_url='https://login.yandex.ru/'
        )

    def authorize(self):
        return redirect(self.service.get_authorize_url(
            response_type='code',
            redirect_uri=self.get_callback_url())
        )

    def callback(self):
        def decode_json(payload):
            return json.loads(payload.decode('utf-8'))

        if 'code' not in request.args:
            return None, None, None

        oauth_session = self.service.get_auth_session(
            data={'code': request.args['code'],
                  'grant_type': 'authorization_code'},
            decoder=decode_json
        )
        me = oauth_session.get('info').json()
        return (me['id'],
                me['emails'][0],
                me['login'])
