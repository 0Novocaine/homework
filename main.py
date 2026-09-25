import redis.asyncio as redis
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter import FastAPILimiter

from src.conf.config import settings
from src.routes import auth, contacts, notes, tags, users

app = FastAPI(
    title="Contacts API",
    description="REST API for contacts with JWT authentication and email confirmation.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(auth.router, prefix="/api")
app.include_router(contacts.router, prefix="/api")
app.include_router(tags.router, prefix="/api")
app.include_router(notes.router, prefix="/api")
app.include_router(users.router, prefix="/api")


@app.on_event('startup')
async def startup() -> None:
    redis_connection = redis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        db=0,
        encoding='utf-8',
        decode_responses=True,
    )
    await redis_connection.ping()
    await FastAPILimiter.init(redis_connection)
    app.state.redis = redis_connection


@app.on_event('shutdown')
async def shutdown() -> None:
    await app.state.redis.aclose()


@app.get("/")
def read_root():
    return {"message": "Contacts API is running"}

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
