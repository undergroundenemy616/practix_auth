from pprint import pprint
import click
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required
from marshmallow import ValidationError

from utils import register_user

from db.pg_db import db
from models import User, History
from schemas import UserLoginSchema, UserSchemaDetailed, UserSchemaUpdate, UserHistorySchema

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


@accounts.route('/user-history', methods=['GET'])
@jwt_required()
def get_user_history():
    login = get_jwt_identity()
    user = User.query.filter_by(login=login).first()
    if not user:
        return jsonify({
            'error': 'Ошибка доступа',
        }), 403
    paginated_user_history = History.get_paginated_data(page=request.args.get('page'),
                                                        count=request.args.get('count'),
                                                        schema=UserHistorySchema,
                                                        filtered_kwargs={'user_id': user.id})
    return jsonify(paginated_user_history), 200


@accounts.after_request
def after_request_func(response):
    if request.path.endswith('register'):
        return response
    login = request.get_json().get('login')
    if not login:
        login = get_jwt_identity()
    user = User.query.filter_by(login=login).first()
    if user:
        history = UserHistorySchema().load({"user_id": str(user.id),
                                            "user_agent": str(request.user_agent),
                                            "info": f"{request.method} {request.path}"})
        db.session.add(history)
        db.session.commit()
    return response
