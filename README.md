# Contacts API

REST API для работы с контактами. Проект написан на FastAPI, использует PostgreSQL, JWT-авторизацию, Redis и Cloudinary.

Пользователь видит и изменяет только свои контакты.

## Запуск

1. Создание файла с настройками:

```bash
cp .env.example .env
```

2. Заполнение файла `.env`. Обязательные параметры:

- `POSTGRES_PASSWORD` пароль базы данных;
- `JWT_SECRET_KEY` случайная строка длиной не меньше 32 символов;
- настройки почты (`MAIL_*`) для подтверждения email.

Для загрузки аватаров также указываются переменные `CLOUDINARY_*`.

3. Сборка и запуск проекта:

```bash
docker compose up --build -d
```

Миграции применяются автоматически. Документация Swagger будет доступна по адресу:

```text
http://localhost:8000/docs
```

При занятом порте 8000 в `.env` можно указать, например, `API_PORT=8001`. В этом случае Swagger будет доступен по адресу `http://localhost:8001/docs`.

## Как пользоваться API

1. Регистрация пользователя: `POST /api/auth/signup`.
2. Подтверждение e-mail по ссылке из письма.
3. Аутентификация через `POST /api/auth/login` с получением `access_token` и `refresh_token`.
4. Авторизация в Swagger: кнопка **Authorize**, значение = `access_token`.
5. Работа с маршрутами контактов после авторизации.

Обновление пары токенов выполняется через `POST /api/auth/refresh`. Refresh-токен передаётся в заголовке:

```text
Authorization: Bearer <refresh_token>
```

Контакты ограничены до 10 запросов в минуту для одного пользователя. Это относится и к созданию контакта.

## Аватар

Загрузка аватара после авторизации выполняется через:

```text
PATCH /api/users/avatar
```

В Swagger файл изображения передаётся в поле `file`. Для работы маршрута требуется заполненная конфигурация Cloudinary в `.env`.

Профиль текущего пользователя: `GET /api/users/me/`.

## Тестовые контакты

```bash
docker compose exec api poetry run python seed.py
```

Команда создаёт 20 контактов пользователя `seed@example.com`. Пароль: `seedpassword`.

## Проверка проекта

В проекте используются:

- unit-тесты репозиториев `notes`, `tags`, `users` и `contacts` на `unittest`;
- функциональные тесты маршрутов аутентификации и тегов на `pytest`;
- документация исходного кода на Sphinx.

Запуск всех тестов:

```bash
poetry run python -m pytest
```

Проверка покрытия кода тестами:

```bash
poetry run python -m pytest --cov=src --cov-report=term-missing
```

Текущее общее покрытие тестами = 74%.

Сборка HTML-документации Sphinx:

```bash
poetry run sphinx-build -b html -W docs/source docs/_build/html
```

После сборки главная страница документации находится в файле `docs/_build/html/index.html`.

## Полезные команды

```bash
docker compose ps
docker compose logs -f api
docker compose down
```

Удаление контейнеров вместе с данными PostgreSQL:

```bash
docker compose down -v
```
