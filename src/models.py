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


class Permission(db.Model):
    __tablename__ = 'permission'
    id = db.Column(UUID(as_uuid=True), primary_key=True)
    name = db.Column(db.String, unique=True)

    def __str__(self):
        return f'<Permission {self.name}>'


class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(UUID(as_uuid=True), primary_key=True)
    name = db.Column(db.String, unique=True)
    description = db.Column(db.String)
    permissions = db.relationship('Permission', secondary=role_permission,
                                  backref=db.backref('roles', lazy='dynamic'))
    users = db.relationship('User', backref="role")

    def __str__(self):
        return f'<Role {self.name}>'


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
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


class History(db.Model):
    __tablename__ = 'history'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = db.Column('user_id', UUID(as_uuid=True), db.ForeignKey('user.id', ondelete='CASCADE'))
    user_agent = db.Column(db.String)
    date = db.Column(db.DateTime(), default=datetime.utcnow)
    info = db.Column(db.String)

    def __str__(self):
        return f'<History {self.user_id}>'
