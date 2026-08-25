# Contacts API — Homework 12

FastAPI with JWT authentication and owner-only access.

## Run with Docker

```bash
cp .env.example .env
# Set strong POSTGRES_PASSWORD and JWT_SECRET_KEY values in .env
docker compose up --build -d
```

The API applies Alembic migrations automatically. Open Swagger at
`http://localhost:8000/docs`.

## Authentication

Register user with `POST /api/auth/signup`:

```json
{
  "username": "anna_user",
  "email": "anna@example.com",
  "password": "secure-password"
}
```

Authenticate with `POST /api/auth/login` using JSON:

```json
{
  "email": "anna@example.com",
  "password": "secure-password"
}
```

The response contains an `access_token` and `refresh_token`. Use the access token
for every contacts request:

```text
Authorization: Bearer <access_token>
```

## Test data

```bash
docker compose exec api poetry run python seed.py
```

This creates 20 contacts. The test password is
`seedpassword`.

## Useful commands
