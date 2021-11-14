import logging
from pprint import pprint

import click

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token
from marshmallow import ValidationError

from db.pg_db import db

from models import User, History
from schemas import UserLoginSchema
from utils import register_user


accounts = Blueprint('accounts', __name__)
logging.basicConfig(level=logging.INFO)


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
            'message': f'User {login} was created',
            'access_token': access_token,
            'refresh_token': refresh_token
        }, 201)

