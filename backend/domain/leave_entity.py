from enum import Enum
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Enum as SAEnum
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class LeaveStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

# --- SQLAlchemy Models ---
class EmployeeModel(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    role = Column(String(50), nullable=False)
    remaining_leave_days = Column(Integer, default=0)

class LeaveRequestModel(Base):
    __tablename__ = "leave_requests"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, nullable=False)
    days = Column(Integer, nullable=False)
    status = Column(SAEnum(LeaveStatus), default=LeaveStatus.PENDING)

# --- Pydantic Schemas ---
class EmployeeCreateSchema(BaseModel):
    name: str
    role: str
    remaining_leave_days: int = 0

class EmployeeSchema(BaseModel):
    id: int
    name: str
    role: str
    remaining_leave_days: int

    class Config:
        from_attributes = True

class LeaveRequestSchema(BaseModel):
    id: int
    employee_id: int
    days: int
    status: LeaveStatus

    class Config:
        from_attributes = True
