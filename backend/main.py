from fastapi import FastAPI
from backend.api.leave_router import router as leave_router
from backend.api.employee_router import router as employee_router
from backend.domain.leave_entity import Base
from backend.infrastructure.database import engine

app = FastAPI(title="HRM MVP")

# Tạo bảng (do dùng SQLite memory/local file đơn giản)
Base.metadata.create_all(bind=engine)

# Đăng ký Router
app.include_router(leave_router)
app.include_router(employee_router)

@app.get("/")
def root():
    return {"message": "HRM Backend API is running"}

# Code chạy `uvicorn backend.main:app --reload`
