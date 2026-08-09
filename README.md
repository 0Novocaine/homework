# Contacts API

REST API for managing contacts, built with FastAPI, SQLAlchemy, PostgreSQL, and Pydantic.

Quick start and test data

```bash
# Download the homework branch
git clone --branch hw-11 --single-branch https://github.com/0Novocaine/homework.git
cd homework

# Create local PostgreSQL settings and set a secure password in .env
cp .env.example .env

# Build and start the API and PostgreSQL
docker compose up --build -d

# Create 20 fake contacts with Faker
docker compose exec api poetry run python seed.py

# View all contacts
curl http://localhost:8000/api/contacts/


```
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

###Example request body:

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
