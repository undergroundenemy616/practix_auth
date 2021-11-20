import uuid

from sqlalchemy.dialects.postgresql import UUID

from db.pg_db import db


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
