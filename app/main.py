from fastapi import FastAPI

from app.api.routers import auth, comments, photos, users

app = FastAPI(
    title="PhotoShare API",
    version="1.0.0",
    description="REST API for uploading, transforming, and discussing photos.",
)
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(photos.router, prefix="/api")
app.include_router(comments.router, prefix="/api")


@app.get("/health", tags=["System"], summary="Check application availability")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
