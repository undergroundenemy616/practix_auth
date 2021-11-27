from datetime import datetime

from sqlalchemy.dialects.postgresql import UUID
from werkzeug.security import generate_password_hash, check_password_hash

from db.pg_db import db
from models.mixins import BaseModelMixin
from models.rbac import Role
from sqlalchemy import UniqueConstraint


def create_partition(target, connection, **kw) -> None:
    """ creating partition by user_sign_in """
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "user_sign_in_smart" PARTITION OF "users_sign_in" FOR VALUES IN ('smart')"""
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "user_sign_in_mobile" PARTITION OF "users_sign_in" FOR VALUES IN ('mobile')"""
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "user_sign_in_web" PARTITION OF "users_sign_in" FOR VALUES IN ('web')"""
    )


class User(db.Model, BaseModelMixin):
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

    @classmethod
    def check_permission(cls, login, required_permission):
        user = cls.query.filter_by(login=login).first()
        if not user:
            return False
        user_role = Role.query.filter_by(id=user.role_id).first()
        if required_permission not in user_role.permissions_names:
            return False
        return True

    def __str__(self):
        return f'<User {self.login}>'


class History(db.Model, BaseModelMixin):
    __tablename__ = 'users_sign_in'
    __table_args__ = (
        UniqueConstraint('id', 'user_device_type'),
        {
            'postgresql_partition_by': 'LIST (user_device_type)',
            'listeners': [('after_create', create_partition)],
        }
    )
    user_id = db.Column('user_id', UUID(as_uuid=True), db.ForeignKey('user.id', ondelete='CASCADE'))
    user_agent = db.Column(db.String)
    date = db.Column(db.DateTime(), default=datetime.utcnow)
    info = db.Column(db.String)
    user_device_type = db.Column(db.Text, primary_key=True)

    def __str__(self):
        return f'<History {self.user_id}>'
