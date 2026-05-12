from backend.domain.leave_entity import EmployeeModel

class LeaveDomainService:
    # Cấp 3: Chứa business rule - Kiểm tra số ngày nghỉ còn lại có đủ không
    def can_approve_leave(self, employee: EmployeeModel, requested_days: int) -> bool:
        if requested_days <= 0:
            return False
        return employee.remaining_leave_days >= requested_days
