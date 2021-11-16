import uuid
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
from werkzeug.security import generate_password_hash, check_password_hash

from db.pg_db import db

role_permission = db.Table(
    'role_permission',
    db.Column('role_id', UUID(as_uuid=True), db.ForeignKey('role.id')),
    db.Column('permission_id', UUID(as_uuid=True), db.ForeignKey('permission.id'))
)


class BaseModel(object):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.id}>'

    @classmethod
    def get_paginated_data(cls, page: int or None, count: int or None, schema, filtered_kwargs=None) -> list:
        page = int(page) if str(page).isdigit() else 1
        count = int(count) if str(count).isdigit() else 20
        if not filtered_kwargs:
            objects = db.session.query(cls).all()
        else:
            objects = db.session.query(cls).filter_by(**filtered_kwargs)
        serialized_paginated_objects = schema().dump(objects, many=True)[count * (page - 1):count * page]
        return serialized_paginated_objects


class Permission(db.Model, BaseModel):
    __tablename__ = 'permission'

    name = db.Column(db.String, unique=True)

    def __str__(self):
        return f'<Permission {self.name}>'


class Role(db.Model, BaseModel):
    __tablename__ = 'role'

    name = db.Column(db.String, unique=True)
    description = db.Column(db.String)
    permissions = db.relationship('Permission', secondary=role_permission,
                                  backref=db.backref('roles', lazy='dynamic'))
    users = db.relationship('User', backref="role")

    def __str__(self):
        return f'<Role {self.name}>'


class User(db.Model, BaseModel):
    __tablename__ = 'user'

    login = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    name = db.Column(db.String)
    email = db.Column(db.String, unique=True)
    created_at = db.Column(db.DateTime(), default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)
    history = db.relationship('History', backref='user')
    role_id = db.Column(UUID(as_uuid=True), db.ForeignKey('role.id', ondelete='SET NULL'))

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __str__(self):
        return f'<User {self.login}>'


class History(db.Model, BaseModel):
    __tablename__ = 'history'

    user_id = db.Column('user_id', UUID(as_uuid=True), db.ForeignKey('user.id', ondelete='CASCADE'))
    user_agent = db.Column(db.String)
    date = db.Column(db.DateTime(), default=datetime.utcnow)
    info = db.Column(db.String)

    def __str__(self):
        return f'<History {self.user_id}>'
