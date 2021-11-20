from datetime import datetime

from sqlalchemy.dialects.postgresql import UUID
from werkzeug.security import generate_password_hash, check_password_hash

from db.pg_db import db
from models.mixins import BaseModel
from models.rbac import Role


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


class History(db.Model, BaseModel):
    __tablename__ = 'history'

    user_id = db.Column('user_id', UUID(as_uuid=True), db.ForeignKey('user.id', ondelete='CASCADE'))
    user_agent = db.Column(db.String)
    date = db.Column(db.DateTime(), default=datetime.utcnow)
    info = db.Column(db.String)

    def __str__(self):
        return f'<History {self.user_id}>'
