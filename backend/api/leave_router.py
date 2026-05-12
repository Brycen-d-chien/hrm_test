from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.infrastructure.leave_repository import LeaveRepository
from backend.domain.leave_service import LeaveDomainService
from backend.application.approve_leave_usecase import ApproveLeaveUseCase
from backend.infrastructure.database import get_db
from backend.infrastructure.auth import require_admin

router = APIRouter(prefix="/api/leaves", tags=["Leaves"])

# SOLID DI Dependencies Setup bằng `Depends` của FastAPI (giảm coupling)
def get_leave_repository(db: Session = Depends(get_db)):
    return LeaveRepository(db)

def get_leave_domain_service():
    return LeaveDomainService()

def get_approve_leave_usecase(
    repo: LeaveRepository = Depends(get_leave_repository),
    domain_service: LeaveDomainService = Depends(get_leave_domain_service)
):
    return ApproveLeaveUseCase(repo, domain_service)

# Cấp 1: Router nhận request
@router.post("/{leave_id}/approve")
def approve_leave(
    leave_id: int, 
    usecase: ApproveLeaveUseCase = Depends(get_approve_leave_usecase),
    admin_user: dict = Depends(require_admin)
):
    result = usecase.execute(leave_id)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result
