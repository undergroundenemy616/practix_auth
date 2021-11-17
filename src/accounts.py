from pprint import pprint
import click
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required
from marshmallow import ValidationError

from utils import register_user

from models import User
from schemas import UserLoginSchema, UserSchemaDetailed, UserSchemaUpdate
from db.pg_db import db
from db.redis_db import redis_db

accounts = Blueprint('accounts', __name__)


@accounts.cli.command("createsuperuser")
@click.argument("login")
@click.argument("password")
def create_user(login, password):
    result = register_user(login, password, superuser=True)
    pprint(result[0])


@accounts.route('/register', methods=['POST'])
def register():
    return register_user(**request.get_json())


@accounts.route('/login', methods=['POST'])
def sign_in():
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
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 200

    return jsonify({
        'error': 'Неверная пара логин-пароль',
    }), 403


@accounts.route('/update', methods=['GET', 'POST'])
@jwt_required()
def update():
    login = get_jwt_identity()
    user = User.query.filter_by(login=login).first()

    if not user:
        return jsonify({
            'error': 'Ошибка доступа',
        }), 403

    if request.method == "GET":
        result = UserSchemaDetailed().dumps(user, ensure_ascii=False)
        return result

    try:
        new_user_info = UserSchemaUpdate().load(request.get_json(), partial=True)
    except ValidationError as e:
        return jsonify(e.messages), 400

    if new_login := new_user_info.get('login', None):
        if User.query.filter(User.login == new_login, User.id != user.id).first():
            return jsonify({'error': 'Пользователь с таким login уже зарегистрирован'}), 400

    if new_password := new_user_info.pop('password', None):
        user.set_password(new_password)

    User.query.filter_by(id=user.id).update(new_user_info)
    db.session.commit()

    return jsonify({
        'message': f'Пользователь {login} успешно обновлен',
    }), 200


@accounts.route('/logout', methods=['DELETE'])
@jwt_required
def logout():
    login = get_jwt_identity()
    user = User.query.filter_by(login=login).first()

    jti = get_jwt_identity
    redis_db(jti, "")
    return jsonify({
        'message': f'Сеанс пользователя {login} успешно завершен'
    }), 200
