from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required, get_jwt
from marshmallow import ValidationError

import redis
from db.pg_db import db
from db.redis_db import redis_db
from models import User, History
from schemas import UserLoginSchema, UserSchemaDetailed, UserSchemaUpdate

accounts = Blueprint('accounts', __name__)


@accounts.route('/register', methods=['POST'])
def register():
    try:
        user = UserLoginSchema().load(request.get_json())
    except ValidationError as e:
        return jsonify(e.messages), 400
    else:
        login = user['login']
        password = user['password']
        if User.query.filter_by(login=login).first():
            return jsonify({'error': 'Пользователь с таким login уже зарегистрирован'}), 400
        user = User(login=login)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        access_token = create_access_token(identity=login)
        refresh_token = create_refresh_token(identity=login)
        return jsonify({
            'message': f'Пользователь {login} успешно зарегистрирован',
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 201


@accounts.route('/login', methods=['POST'])
def sign_in():
    try:
        user_try = UserLoginSchema().load(request.get_json())
    except ValidationError as e:
        return jsonify(e.messages), 400
    else:
        login_try = user_try['login']
        password_try = user_try['password']
        user = User.query.filter_by(login=login_try).first()
        if user and user.check_password(password_try):
            login = login_try
            access_token = create_access_token(identity=login)
            refresh_token = create_refresh_token(identity=login)

            user_agent = request.headers.get('User-Agent')
            history_entry = History(user_id=user.id,
                                    user_agent=user_agent,
                                    info='User logged in')
            db.session.add(history_entry)
            db.session.commit()

            return jsonify({
                'access_token': access_token,
                'refresh_token': refresh_token
            }), 200
        else:
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
    else:
        try:
            new_user_info = UserSchemaUpdate().load(request.get_json(), partial=True)
        except ValidationError as e:
            return jsonify(e.messages), 400
        else:
            if new_login := new_user_info.get('login', None):
                if User.query.filter(User.login == new_login, User.id != user.id).first():
                    return jsonify({'error': 'Пользователь с таким login уже зарегистрирован'}), 400
            if new_password := new_user_info.pop('password', None):
                user.set_password(new_password)

            User.query.filter_by(id=user.id).update(new_user_info)

            user_agent = request.headers.get('User-Agent')
            history_entry = History(user_id=user.id,
                                    user_agent=user_agent,
                                    info='User info updated')
            db.session.add(history_entry)
            db.session.commit()

            return jsonify({
                'message': f'Пользователь {login} успешно обновлен',
            }), 200


@accounts.route('/logout', methods=['DELETE'])
@jwt_required
def logout():
    login = get_jwt_identity()
    user = User.query.filter_by(login=login).first()

    user_agent = request.headers.get('User-Agent')
    history_entry = History(user_id=user.id,
                            user_agent=user_agent,
                            info='User logged off')
    db.session.add(history_entry)
    db.session.commit()

    jti = get_jwt()["jti"]
    redis_db(jti, "", ex=EXPIRES)
    return jsonify({
        'message': f'Сеанс пользователя {login} успешно завершен'
    }), 200

