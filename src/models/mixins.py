import uuid

from sqlalchemy.dialects.postgresql import UUID

from db.pg_db import db


class BaseModelMixin(object):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.id}>'
