import logging
from datetime import datetime

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token
from marshmallow import ValidationError

from db.pg_db import db
from models import User
from schemas import UserLoginSchema

accounts = Blueprint('accounts', __name__)
logging.basicConfig(level=logging.INFO)


@accounts.route('/register', methods=['POST'])
def register():
    try:
        user = UserLoginSchema().load(request.get_json())
    except ValidationError as e:
        return jsonify(e.messages, 400)
    else:
        login = user['login']
        password = user['password']
        if User.query.filter_by(login=login).first() is not None:
            return jsonify({'error': 'Пользователь с таким login уже зарегистрирован'}, 400)
        try:
            user = User(login=login)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            access_token = create_access_token(identity=login)
            refresh_token = create_refresh_token(identity=login)
            return jsonify({
                'message': f'User {login} was created',
                'access_token': access_token,
                'refresh_token': refresh_token
            }, 201)
        except Exception as e:
            logging.error(f'Пользователь {login} не зарегистрирован: {e}')
            return jsonify({'error': 'Ошибка сервера'}, 500)
