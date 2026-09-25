# Contacts API

REST API для работы с контактами.

## Запуск

1. Создание файла с настройками:

```bash
cp .env.example .env
```

2. Откройте `.env`, вставьте свои данніе:

- `POSTGRES_PASSWORD` — пароль базы данных;
- `JWT_SECRET_KEY` — случайная строка длиной не меньше 32 символов;
- настройки почты (`MAIL_*`) — для подтверждения email.

Для загрузки аваторов, дополнительно заполните переменные `CLOUDINARY_*`.

3. Сбор и запуск проекта:

```bash
docker compose up --build -d
```

Документация Swagger на адресе:

```text
http://localhost:8000/docs
```

## Как пользоваться API

1. Зарегистрируйте пользователя: `POST /api/auth/signup`.
2. Подтвердите email по ссылке из письма.
3. Войдите через `POST /api/auth/login` и получите `access_token` и `refresh_token`.
4. В Swagger нажмите **Authorize** и вставьте `access_token`.

Для обновления пары токенов используйте `POST /api/auth/refresh` и передавайте refresh-токен в заголовке:

```text
Authorization: Bearer <refresh_token>
```

Контакты ограничены до 10 запросов в минуту для одного пользователя.

## Аватар

После авторизации аватар можно загрузить через:

```text
PATCH /api/users/avatar
```

В Swagger выберите файл изображения в поле `file`. Для этого нужен заполненный Cloudinary в `.env`.
Профиль текущего пользователя: `GET /api/users/me/`.

## Тестовые контакты

```bash
docker compose exec api poetry run python seed.py
```

Команда создаст 20 контактов пользователя `seed@example.com`. Пароль: `seedpassword`.

