
from db.pg_db import db
from models.mixins import BaseModelMixin


class Role(db.Model, BaseModelMixin):
    __tablename__ = 'role'

    name = db.Column(db.String, unique=True, nullable=False)
    description = db.Column(db.String)
    users = db.relationship('accounts.User', backref='role')

    def __str__(self):
        return f'<Role {self.name}>'


