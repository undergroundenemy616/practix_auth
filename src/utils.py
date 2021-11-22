import functools
from http import HTTPStatus

from flask import jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity
from marshmallow import ValidationError
from werkzeug.exceptions import abort

from db.pg_db import db
from models.accounts import User
from models.rbac import Role
from schemas.accounts import UserLoginSchema


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


def check_permission(required_permission: str):
    def check_admin_inner(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            login = get_jwt_identity()
            if not User.check_permission(login=login, required_permission=required_permission):
                return jsonify({'type': 'error', 'message': 'Доступ запрещен'}), HTTPStatus.FORBIDDEN
            return f(*args, **kwargs)

        return wrapper

    return check_admin_inner


def get_login_and_user_or_403():
    login = get_jwt_identity()
    user = User.query.filter_by(login=login).first()
    if not user:
        abort(403)
    return login, user

