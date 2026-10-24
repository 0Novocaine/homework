# PhotoShare

PhotoShare — навчальний REST API-застосунок для завантаження та обробки фотографій. 
Користувач реєструється, завантажує світлину, додає теги, створює посилання на оброблене зображення та QR-код. 
Інші користувачі можуть залишати коментарі.

## Можливості

- реєстрація й вхід за JWT-токеном;
- ролі `USER`, `MODERATOR`, `ADMIN`; перший користувач автоматично отримує `ADMIN`;
- блокування та розблокування користувачів адміністратором;
- завантаження JPEG, PNG і WebP до 5 МБ;
- редагування опису та видалення власних світлин;
- до п’яти унікальних тегів на одну світлину;
- зберігання зображень у Cloudinary;
- resize, crop, grayscale, blur і rotation;
- QR-код для посилання на оброблене зображення;
- коментарі, публічні профілі та Swagger-документація.

## Технології

Python 3.11+, FastAPI, PostgreSQL, SQLAlchemy 2, Alembic, JWT, bcrypt, Cloudinary, Docker Compose, pytest і pytest-cov.

## Архітектура

```text
app/
  api/             HTTP-маршрути та залежності FastAPI
  core/            конфігурація й безпека
  db/              підключення до бази даних
  integrations/    Cloudinary та генерація QR-кодів
  models/          ORM-моделі
  repositories/    SQLAlchemy-запити
  schemas/         Pydantic-схеми API
  services/        бізнес-логіка
alembic/           міграції бази даних
tests/             автоматичні тести
```

Логіка розділена за принципом `Router → Service → Repository → Database`. 
Роутери працюють з HTTP, сервіси містять бізнес-правила, а репозиторії ізолюють запити до бази даних.

Основні моделі: `User`, `Photo`, `Tag`, `Comment`, `PhotoTransformation`. 
Між `Photo` і `Tag` використовується зв’язок many-to-many; коментарі 
й перетворення мають зв’язок one-to-many зі світлиною.

## Швидкий запуск у Docker

1. Створіть локальний файл налаштувань:

   ```bash
   cp .env.example .env
   ```

2. Заповніть `.env`:

   ```env
   CLOUDINARY_CLOUD_NAME=...
   CLOUDINARY_API_KEY=...
   CLOUDINARY_API_SECRET=...
   SECRET_KEY=довгий_випадковий_рядок
   ```

3. Запустіть застосунок:

   ```bash
   docker compose up --build
   ```

Після старту:

- API: `http://localhost:8000`;
- Swagger: `http://localhost:8000/docs`;
- перевірка стану: `http://localhost:8000/health`.

Контейнер автоматично застосовує міграції Alembic.

## Локальний запуск без Docker

Потрібні Python 3.11+ і PostgreSQL. У `.env` вкажіть адресу бази даних у `DATABASE_URL`.

```bash
python -m venv .venv
.venv/bin/pip install -e '.[dev]'
.venv/bin/alembic upgrade head
.venv/bin/uvicorn app.main:app --reload
```

## Основні маршрути

| Дія | Маршрут |
| --- | --- |
| Реєстрація | `POST /api/auth/register` |
| Вхід | `POST /api/auth/login` |
| Власний профіль | `GET`, `PATCH /api/users/me` |
| Публічний профіль | `GET /api/users/{username}` |
| Блокування або розблокування | `PATCH /api/users/{username}/active` |
| Завантаження світлини | `POST /api/photos` |
| Перегляд, редагування, видалення | `GET`, `PATCH`, `DELETE /api/photos/{photo_id}` |
| Перетворення та QR-код | `POST /api/photos/{photo_id}/transformations` |
| Коментарі | `GET`, `POST /api/photos/{photo_id}/comments` |

Для захищених маршрутів у Swagger натисніть **Authorize** та вставте отриманий токен у форматі `Bearer ваш_токен`.

## Права доступу

- `USER` працює зі своїми фото й коментарями;
- `MODERATOR` і `ADMIN` можуть видаляти коментарі;
- `ADMIN` може редагувати або видаляти всі фото, а також блокувати користувачів;
- неактивний користувач не може увійти або виконувати захищені запити.

## Міграції та тести

```bash
.venv/bin/alembic upgrade head
.venv/bin/pytest
```
