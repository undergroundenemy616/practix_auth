import re

from marshmallow import fields, Schema, ValidationError


def validate_password(password):
    pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{8,}$'

    if not re.match(pattern, password):
        raise ValidationError('Пароль должен иметь буквы в обоих регистрах, цифры и быть длиной не менее 8 символов.')


def must_not_be_blank(data):
    if not data:
        raise ValidationError("Поле должно быть заполнено.")


class UserUpdateSchema(Schema):
    login = fields.String(required=True, error_messages={'required': 'Поле должно быть заполнено.'},
                          validate=must_not_be_blank)
    password = fields.String(required=True, error_messages={'required': 'Поле должно быть заполнено.'},
                             validate=validate_password)
    name = fields.String()
    email = fields.Email()


class UserLoginSchema(Schema):
    login = fields.String(required=True, error_messages={'required': 'Поле должно быть заполнено.'},
                          validate=must_not_be_blank)
    password = fields.String(required=True, error_messages={'required': 'Поле должно быть заполнено.'},
                             validate=validate_password)
