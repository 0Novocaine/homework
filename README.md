# Contacts API — secure configuration

FastAPI contacts service with PostgreSQL, JWT authentication and owner-only access.

## Run with Docker

```bash
cp .env.example .env
# Set strong POSTGRES_PASSWORD and JWT_SECRET_KEY values in .env.
# Add SMTP values for email confirmation.
# Add Cloudinary values to enable avatar uploads.
docker compose up --build -d
```

If port 8000 is already used by another project, set `API_PORT=8001` in `.env`.

The API applies Alembic migrations automatically. Open Swagger at
`http://localhost:8000/docs`.

Docker starts PostgreSQL and Redis. The endpoint `GET /api/contacts/` is
limited to 10 requests per minute. CORS permits origins specified by
`CORS_ORIGINS` (comma-separated), defaulting to `http://localhost:3000`.

## User profile

`GET /api/users/me/` returns the authenticated user's profile.

`PATCH /api/users/avatar` accepts an image in the multipart field `file` and
stores it in Cloudinary. Set `CLOUDINARY_NAME`, `CLOUDINARY_API_KEY`, and
`CLOUDINARY_API_SECRET` in `.env` before using this route.

## Authentication

Register a user with `POST /api/auth/signup`:

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

The response contains an `access_token` and a `refresh_token`. Use the access token
for every contacts request:

```text
Authorization: Bearer <access_token>
```

Use `POST /api/auth/refresh` and pass the refresh token in the same header to receive
a new token pair. Contacts from another user are never returned or changed.

## Test data

```bash
docker compose exec api poetry run python seed.py
```

This creates 20 contacts owned by `seed@example.com`. The test password is
`seedpassword`.

## Useful commands

```bash
docker compose ps
docker compose logs -f api
docker compose down
docker compose down -v  # also deletes PostgreSQL data
```
