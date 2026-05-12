from backend.infrastructure.leave_repository import LeaveRepository
from backend.domain.leave_service import LeaveDomainService
from backend.domain.leave_entity import LeaveStatus

class ApproveLeaveUseCase:
    # Cấp 2: Chứa orchestration logic, phụ thuộc Repository & DomainService (SOLID - DI)
    def __init__(self, repo: LeaveRepository, domain_service: LeaveDomainService):
        self.repo = repo
        self.domain_service = domain_service

    def execute(self, leave_request_id: int) -> dict:
        leave_request = self.repo.get_leave_request(leave_request_id)
        if not leave_request:
            return {"success": False, "message": "Không tìm thấy đơn."}
        
        if leave_request.status != LeaveStatus.PENDING:
            return {"success": False, "message": "Đơn đã được xử lý."}

        employee = self.repo.get_employee(leave_request.employee_id)
        if not employee:
            return {"success": False, "message": "Không tìm thấy nhân viên."}

        # Gọi Domain Service để kiểm tra business rules
        if not self.domain_service.can_approve_leave(employee, leave_request.days):
            return {"success": False, "message": "Nhân viên không đủ ngày nghỉ phép."}

        # Orchestrate cập nhật repository
        self.repo.update_leave_status(leave_request.id, LeaveStatus.APPROVED)
        self.repo.update_employee_remaining_days(employee.id, leave_request.days)

        return {"success": True, "message": "Duyệt thành công!"}
