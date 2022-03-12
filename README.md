# Репозиторий Async API:

https://github.com/undergroundenemy616/practix_async_api

Сервисы взаимодействуют по протоколу gRPC. Сервис Async API использует декоратор для представлений, 
включающий запрос к Auth сервису для проверки роли обращающегося пользователя
(https://github.com/undergroundenemy616/practix_async_api/blob/master/src/auth_grpc/auth_check.py)

Оба сервиса подключены к Jaeger.


## Как запустить проект:

После клонирования проекта локально необходимо выполнить команду:
```
cp template.env .env
```
И передать значения переменным, указанным в появившемся файле .env

Затем выполнить команду:
```
docker-compose up
```

#### Подготовка БД:
```
docker-compose exec auth flask db migrate
docker-compose exec auth flask db upgrade
```

#### Заливка фикстур:
```
docker-compose exec auth flask rbac add_base_data
```

#### Создание суперпользователя:
```
docker-compose exec auth flask accounts createsuperuser <username> <password>
```


#### Запуск тестов:
```
docker-compose -f docker-compose.test.yaml up --build
```


#### API Документация

0.0.0.0:8000/apidocs


| компонент системы AUTH | используемая библиотека |
| -----------------------|-------------------------|
| хранение токенов в redis | redis-py, flask-redis |
| работа с postgresql      | Flask-SQLAlchemy, Flask-Migrate |
| генерация и валидация jwt | flask-jwt-extended |
| SwaggerAPI                | flasgger

