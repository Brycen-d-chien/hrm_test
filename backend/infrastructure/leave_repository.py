from sqlalchemy.orm import Session
from backend.domain.leave_entity import LeaveRequestModel, EmployeeModel, LeaveStatus

class LeaveRepository:
    # Cấp 4: Giao tiếp với Database (SQLite). YAGNI: Không cần Interface vì chỉ dùng 1 DB.
    def __init__(self, db_session: Session):
        self.db = db_session

    def get_leave_request(self, request_id: int) -> LeaveRequestModel:
        return self.db.query(LeaveRequestModel).filter(LeaveRequestModel.id == request_id).first()

    def get_employee(self, employee_id: int) -> EmployeeModel:
        return self.db.query(EmployeeModel).filter(EmployeeModel.id == employee_id).first()

    def update_leave_status(self, request_id: int, status: LeaveStatus):
        req = self.get_leave_request(request_id)
        if req:
            req.status = status
            self.db.commit()

    def update_employee_remaining_days(self, employee_id: int, deduct_days: int):
        emp = self.get_employee(employee_id)
        if emp:
            emp.remaining_leave_days -= deduct_days
            self.db.commit()
