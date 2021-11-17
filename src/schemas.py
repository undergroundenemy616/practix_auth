from marshmallow import Schema, fields, post_load

import validate_functions
from db.pg_db import db
from models import History, Permission, Role, User


class UserSchemaDetailed(Schema):
    login = fields.String()
    name = fields.String()
    email = fields.Email()


class UserSchemaUpdate(UserSchemaDetailed):
    password = fields.String(validate=validate_functions.validate_password)


class UserLoginSchema(Schema):
    login = fields.String(required=True, error_messages={'required': 'Поле должно быть заполнено.'},
                          validate=validate_functions.must_not_be_blank)
    password = fields.String(required=True, error_messages={'required': 'Поле должно быть заполнено.'},
                             validate=validate_functions.validate_password)


class UserHistorySchema(Schema):
    user_id = fields.String(load_only=True)
    user_agent = fields.String()
    date = fields.DateTime(dump_only=True)
    info = fields.String()

    @post_load
    def create_user_history(self, data, **kwargs):
        history = History(**data)
        db.session.add(history)
        db.session.commit()
        return history


class PermissionSchema(Schema):

    id = fields.UUID(dump_only=True)
    name = fields.String(required=True, validate=validate_functions.validate_permission_name)

    @post_load
    def create_permission(self, data, **kwargs):
        permission = Permission(**data)
        db.session.add(permission)
        db.session.commit()
        return permission


class RoleSchema(Schema):
    id = fields.UUID()
    name = fields.String(validate=validate_functions.validate_role_name)
    description = fields.String()
    permissions = fields.Nested(PermissionSchema, many=True)


class RoleAssignSchema(Schema):
    role_id = fields.UUID()
    users = fields.List(fields.UUID, validate=validate_functions.validate_exist_users, required=True)

    @post_load
    def assign_role(self, data, **kwargs):
        User.query.filter(User.id.in_([data.pop('users')])).update({'role_id': data['role_id']},
                                                                   synchronize_session=False)
        db.session.commit()
        return


class RoleCreateSchema(RoleSchema):
    id = fields.UUID(dump_only=True)
    name = fields.String(validate=validate_functions.validate_role_name, required=True)
    permissions = fields.List(fields.UUID, validate=validate_functions.validate_exist_permissions)

    @post_load
    def create_role(self, data, **kwargs):
        permissions = data.pop('permissions', None)
        role = Role(**data)
        if permissions:
            permissions = Permission.query.filter(Permission.id.in_([permissions]))
            role.permissions.extend(permissions)
        db.session.add(role)
        db.session.commit()
        return role


class RoleUpdateSchema(RoleSchema):
    permissions = fields.List(fields.UUID, validate=validate_functions.validate_exist_permissions)

    @post_load
    def update_role(self, data, **kwargs):
        permissions = data.pop('permissions', None)
        role = Role.query.filter_by(id=data.pop('id')).first()
        role.update(**data)
        if permissions:
            role.permissions = []
            permissions = Permission.query.filter(Permission.id.in_([permissions]))
            role.permissions.extend(permissions)
        db.session.add(role)
        db.session.commit()
        return role
