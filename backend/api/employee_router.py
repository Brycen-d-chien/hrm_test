from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend.domain.leave_entity import EmployeeSchema, EmployeeCreateSchema, EmployeeModel
from backend.infrastructure.database import get_db
from backend.infrastructure.auth import get_current_user, require_admin

router = APIRouter(prefix="/api/employees", tags=["Employees"])

@router.get("/", response_model=List[EmployeeSchema])
def get_employees(db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    """Admin xem danh sách nhân viên"""
    return db.query(EmployeeModel).all()

@router.get("/me", response_model=EmployeeSchema)
def get_my_info(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Employee xem thông tin của mình"""
    employee = db.query(EmployeeModel).filter(EmployeeModel.id == current_user["id"]).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Không tìm thấy thông tin")
    return employee

@router.post("/", response_model=EmployeeSchema, status_code=201)
def create_employee(employee: EmployeeCreateSchema, db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    """Admin thêm nhân viên"""
    new_employee = EmployeeModel(
        name=employee.name,
        role=employee.role,
        remaining_leave_days=employee.remaining_leave_days
    )
    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)
    return new_employee
