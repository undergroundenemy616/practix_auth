import os
from pathlib import Path


class BaseConfig:
    SECRET_KEY = os.getenv('SECRET_KEY', '')
    DEBUG = False
    # Настройки Redis
    REDIS_HOST = os.getenv('REDIS_HOST', '127.0.0.1')
    REDIS_PORT = os.getenv('REDIS_PORT', 6379)

    # Настройки Postgres
    POSTGRES_DB = os.getenv('POSTGRES_DB', 'auth_database')
    POSTGRES_USER = os.getenv('POSTGRES_USER', 'postgres')
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 1234)
    POSTGRES_HOST = os.getenv('POSTGRES_HOST', '127.0.0.1')
    POSTGRES_PORT = os.getenv('POSTGRES_DB', 5432)

    # Корень проекта
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    SECURITY_PASSWORD_HASH = os.getenv('SECURITY_PASSWORD_HASH', '')
    SECURITY_PASSWORD_SALT = os.getenv('SECURITY_PASSWORD_SALT', '')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentBaseConfig(BaseConfig):
    DEBUG = True


class ProductionBaseConfig(BaseConfig):
    DEBUG = False

