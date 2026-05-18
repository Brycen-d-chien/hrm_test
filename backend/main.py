from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from backend.api.employee_router import router as employee_router
from backend.api.leave_router import router as leave_router
from backend.api.storage_router import router as storage_router
from backend.domain.leave_entity import Base
from backend.infrastructure.database import DATABASE_URL, engine
from backend.infrastructure.db_config import should_auto_create_schema


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as error:
        raise RuntimeError(f"Khong the ket noi database: {error}") from error

    if should_auto_create_schema(DATABASE_URL):
        Base.metadata.create_all(bind=engine)

    yield


app = FastAPI(title="HRM MVP", lifespan=lifespan)

app.include_router(leave_router)
app.include_router(employee_router)
app.include_router(storage_router)


@app.get("/")
def root():
    return {"message": "HRM Backend API is running"}
