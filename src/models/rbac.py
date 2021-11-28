from sqlalchemy.dialects.postgresql import UUID

from db.pg_db import db
from models.mixins import BaseModelMixin

role_permission = db.Table(
    'role_permission',
    db.Column('role_id', UUID(as_uuid=True), db.ForeignKey('role.id')),
    db.Column('permission_id', UUID(as_uuid=True), db.ForeignKey('permission.id'))
)


class Permission(db.Model, BaseModelMixin):
    __tablename__ = 'permission'

    name = db.Column(db.String, unique=True, nullable=False)

    def __str__(self):
        return f'<Permission {self.name}>'


class Role(db.Model, BaseModelMixin):
    __tablename__ = 'role'

    name = db.Column(db.String, unique=True, nullable=False)
    description = db.Column(db.String)
    permissions = db.relationship('Permission', secondary=role_permission,
                                  backref=db.backref('roles', lazy='dynamic'))
    users = db.relationship('accounts.User', backref='role')

    def __str__(self):
        return f'<Role {self.name}>'

    @property
    def permissions_names(self):
        return [permission.name for permission in self.permissions]

