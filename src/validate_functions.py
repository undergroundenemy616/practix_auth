import re

from marshmallow import ValidationError
from models import Role, Permission


def validate_password(password):
    pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{8,}$'

    if not re.match(pattern, password):
        raise ValidationError('Пароль должен иметь буквы в обоих регистрах, цифры и быть длиной не менее 8 символов.')


def must_not_be_blank(data):
    if not data:
        raise ValidationError("Поле должно быть заполнено.")


def validate_role_name(name):
    if Role.query.filter_by(name=name).first():
        raise ValidationError("Роль с такими именем уже существует")


def validate_permission_name(name):
    if Permission.query.filter_by(name=name).first():
        raise ValidationError("Право с такими именем уже существует")


def validate_exist_permissions(permissions):
    for permission_id in permissions:
        permission = Permission.query.filter_by(id=permission_id).first()
        if not permission:
            raise ValidationError(f"Право с id={permission} не существует")