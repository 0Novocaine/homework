# PhotoShare

Навчальний REST API для завантаження, обробки та обговорення фотографій. 
Стек: FastAPI, PostgreSQL, SQLAlchemy, Cloudinary, Docker.

Запуск Docker-контейнерів:

```bash
docker compose up --build
```

Swagger-документація: [http://localhost:8000/docs](http://localhost:8000/docs).

Запуск тестів (після встановлення залежностей проєкту):

```bash
.venv/bin/pytest
```

API підтримує реєстрацію та авторизацію, ролі користувачів, завантаження 
та трансформацію фото, теги, пошук і коментарі. 
Перший зареєстрований користувач отримує роль адміністратора.
