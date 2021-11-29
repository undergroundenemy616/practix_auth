from marshmallow import fields, Schema, post_load

import validate_functions
from models.rbac import  Role


class RoleSchema(Schema):
    id = fields.UUID()
    name = fields.String(validate=validate_functions.validate_role_name)
    description = fields.String()


class RoleAssignSchema(Schema):
    users = fields.List(fields.UUID, validate=validate_functions.validate_exist_users, required=True)


class RoleCreateSchema(RoleSchema):
    id = fields.UUID(dump_only=True)
    name = fields.String(validate=validate_functions.validate_role_name, required=True)

    @post_load
    def create_role(self, data, **kwargs):
        role = Role(**data)
        return role


class RoleUpdateSchema(RoleSchema):

    @post_load
    def update_role(self, data, **kwargs):
        role = Role.query.filter_by(id=data.pop('id')).first()
        role.update(**data)
        return role
