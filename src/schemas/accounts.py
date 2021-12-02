import validate_functions
from marshmallow import Schema, fields, post_load
from models.accounts import History


class UserSchemaDetailed(Schema):
    login = fields.String()
    name = fields.String()
    email = fields.Email()
    password = fields.String(
        validate=validate_functions.validate_password, load_only=True
    )


class UserLoginSchema(Schema):
    login = fields.String(
        required=True,
        error_messages={'required': 'Поле должно быть заполнено.'},
        validate=validate_functions.must_not_be_blank,
    )
    password = fields.String(
        required=True,
        error_messages={'required': 'Поле должно быть заполнено.'},
        validate=validate_functions.validate_password,
    )


class UserHistorySchema(Schema):
    user_id = fields.String(load_only=True)
    user_agent = fields.String()
    date = fields.DateTime(dump_only=True)
    info = fields.String()

    @post_load
    def create_user_history(self, data, **kwargs):
        history = History(**data)
        return history
