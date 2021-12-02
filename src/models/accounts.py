import random
import string
from datetime import datetime

from db.pg_db import db
from sqlalchemy import UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from werkzeug.security import check_password_hash, generate_password_hash

from models.mixins import BaseModelMixin
from models.rbac import Role


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
    updated_at = db.Column(
        db.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow
    )
    history = db.relationship('History', backref='user')
    role_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey('role.id', ondelete='SET NULL')
    )

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    @classmethod
    def check_role(cls, login, required_role):
        user = cls.query.filter_by(login=login).first()
        if not user:
            return False
        user_role = Role.query.filter_by(id=user.role_id).first()
        if user_role.name != required_role:
            return False
        return True

    def __str__(self):
        return f'<User {self.login}>'


class SocialAccount(db.Model, BaseModelMixin):
    __tablename__ = 'social_account'

    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id'), nullable=False)
    user = db.relationship(User, backref=db.backref('social_accounts', lazy=True))

    social_id = db.Column(db.Text, nullable=False)
    social_name = db.Column(db.Text, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('social_id', 'social_name', name='social_pk'),
    )

    def __repr__(self):
        return f'<SocialAccount {self.social_name}:{self.user_id}>'

    @classmethod
    def get_or_create_user(
        cls, social_id: str, social_name: str, username: str, email: str
    ) -> User:
        social_account = cls.query.filter_by(
            social_id=social_id, social_name=social_name
        ).first()
        if social_account:
            user = User.query.filter_by(id=social_account.user_id).first()
        else:
            password = ''.join(random.choice(string.ascii_lowercase) for _ in range(15))
            if User.query.filter_by(login=username).first():
                username = f"{social_id}_{username}"
            role = Role.query.filter_by(name='BaseUser').first().id
            user = User(email=email, login=username, role=role)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            social_account = SocialAccount(
                user_id=user.id, social_id=social_id, social_name=social_name
            )
            db.session.add(social_account)
            db.session.commit()
        return user


class History(db.Model, BaseModelMixin):
    __tablename__ = 'users_sign_in'
    __table_args__ = (
        UniqueConstraint('id', 'user_device_type'),
        {
            'postgresql_partition_by': 'LIST (user_device_type)',
            'listeners': [('after_create', create_partition)],
        },
    )
    user_id = db.Column(
        'user_id', UUID(as_uuid=True), db.ForeignKey('user.id', ondelete='CASCADE')
    )
    user_agent = db.Column(db.String)
    date = db.Column(db.DateTime(), default=datetime.utcnow)
    info = db.Column(db.String)
    user_device_type = db.Column(db.Text, primary_key=True)

    def __str__(self):
        return f'<History {self.user_id}>'
