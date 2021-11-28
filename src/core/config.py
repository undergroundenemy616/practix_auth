import os
from datetime import timedelta


class BaseConfig:
    SECRET_KEY = os.getenv('SECRET_KEY', '')
    DEBUG = False
    TESTING = False
    # Настройки Redis
    REDIS_HOST = os.getenv('REDIS_HOST', '127.0.0.1')
    REDIS_PORT = os.getenv('REDIS_PORT', 6379)
    # База для просроченных токенов
    REDIS_DB = os.getenv('REDIS_DB', 0)
    # База для rate limit
    REDIS_RATE_DB = os.getenv('REDIS_RATE_DB', 1)
    # Настройки Postgres
    POSTGRES_DB = os.getenv('POSTGRES_DB', 'auth_database')
    POSTGRES_USER = os.getenv('POSTGRES_USER', 'postgres')
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 1234)
    POSTGRES_HOST = os.getenv('POSTGRES_HOST', '127.0.0.1')
    POSTGRES_PORT = os.getenv('POSTGRES_DB', 5432)

    # Корень проекта
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JSON_AS_ASCII = False

    REQUEST_LIMIT_PER_MINUTE = 60

class DevelopmentBaseConfig(BaseConfig):
    DEBUG = True


class ProductionBaseConfig(BaseConfig):
    DEBUG = False


class TestBaseConfig(BaseConfig):
    DEBUG = False
    TESTING = True
