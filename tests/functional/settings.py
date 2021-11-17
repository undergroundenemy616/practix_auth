from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    pg_host: str = Field('http://127.0.0.1', env='POSTGRES_HOST')
    pg_port: str = Field('5432', env='ELASTIC_PORT')
    pg_password: str = Field('postgres', env='POSTGRES_PASSWORD')
    pg_user: str = Field('postgres', env='POSTGRES_USER')
    pg_db: str = Field('postgres', env='POSTGRES_DB')

    redis_host: str = Field('http://127.0.0.1', env='REDIS_HOST')
    redis_port: str = Field('6379', env='REDIS_PORT')

    app_host: str = Field('http://127.0.0.1', env='APP_HOST')
    app_port: str = Field('8000', env='APP_PORT')

