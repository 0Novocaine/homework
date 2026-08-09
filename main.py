from fastapi import FastAPI

from src.routes import contacts, notes, tags

app = FastAPI(
    title="Contacts API",
    description="REST API for storing and managing contacts.",
    version="1.0.0",
)

app.include_router(tags.router, prefix='/api')
app.include_router(notes.router, prefix='/api')
app.include_router(contacts.router, prefix="/api")


@app.get("/")
def read_root():
    return {"message": "Hello World"}
