import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.routers import auth, comments, photos, users

app = FastAPI(
    title="PhotoShare API",
    version="1.0.0",
    description="REST API for uploading, transforming, and discussing photos.",
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"error": {"code": exc.status_code, "message": exc.detail}})


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    """Return validation failures in the same envelope as other expected API errors."""
    return JSONResponse(
        status_code=422,
        content={"error": {"code": 422, "message": "Validation error", "details": [
            {"loc": list(error["loc"]), "msg": error["msg"], "type": error["type"]}
            for error in exc.errors()
        ]}},
    )


app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(photos.router, prefix="/api")
app.include_router(comments.router, prefix="/api")


@app.get("/health", tags=["System"], summary="Check application availability")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
