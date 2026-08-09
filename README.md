# Contacts API

REST API for managing contacts, built with FastAPI, SQLAlchemy, PostgreSQL, and Pydantic.

## Run with Docker

Prerequisite: Docker Desktop (or Docker Engine with Docker Compose).

1. Copy the example settings: `cp .env.example .env`.
2. Change `POSTGRES_PASSWORD` in `.env`.
3. Start the whole project: `docker compose up --build -d`.

The API container automatically applies database migrations once PostgreSQL is healthy.
Open Swagger at `http://127.0.0.1:8000/docs`.

Useful commands:

```bash
docker compose logs -f api      # API logs
docker compose down             # stop containers, keep database data
docker compose down -v          # stop containers and delete database data
```

## Run locally

1. Create a PostgreSQL database and set `DATABASE_URL`, for example:
   `postgresql+psycopg2://postgres:password@localhost:5432/contacts_db`.
2. Install dependencies: `poetry install --no-root`.
3. Apply migrations: `poetry run alembic upgrade head`.
4. Start the server: `poetry run uvicorn main:app --reload`.

Interactive API documentation is available at `http://127.0.0.1:8000/docs`.

## Contacts endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| POST | `/api/contacts/` | Create a contact |
| GET | `/api/contacts/` | List contacts (`skip`, `limit`) |
| GET | `/api/contacts/{contact_id}` | Get one contact |
| PUT | `/api/contacts/{contact_id}` | Update a contact |
| DELETE | `/api/contacts/{contact_id}` | Delete a contact |
| GET | `/api/contacts/search/?query=ann` | Search by first name, last name, or email |
| GET | `/api/contacts/upcoming-birthdays/` | Contacts with birthdays within seven days |

Example request body:

```json
{
  "first_name": "Anna",
  "last_name": "Kovalenko",
  "email": "anna@example.com",
  "phone": "+380501234567",
  "birthday": "1995-08-15",
  "additional_data": "Friend from university"
}
```
