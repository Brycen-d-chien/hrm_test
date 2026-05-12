import pytest
from unittest.mock import MagicMock
from backend.application.approve_leave_usecase import ApproveLeaveUseCase
from backend.domain.leave_entity import LeaveStatus

def test_execute_success():
    # 1. Setup mocks (MagicMock) cho test UseCase cục bộ
    mock_repo = MagicMock()
    mock_domain_service = MagicMock()

    # 2. Mock Dữ Liệu
    mock_leave_request = MagicMock()
    mock_leave_request.id = 1
    mock_leave_request.employee_id = 100
    mock_leave_request.days = 2
    mock_leave_request.status = LeaveStatus.PENDING

    mock_employee = MagicMock()
    mock_employee.id = 100

    # Cấu hình giá trị trả về cho Mocks
    mock_repo.get_leave_request.return_value = mock_leave_request
    mock_repo.get_employee.return_value = mock_employee
    mock_domain_service.can_approve_leave.return_value = True

    # 3. Inject Mocks vào UseCase
    usecase = ApproveLeaveUseCase(repo=mock_repo, domain_service=mock_domain_service)

    # 4. Act
    result = usecase.execute(1)

    # 5. Assert
    assert result["success"] is True
    assert result["message"] == "Duyệt thành công!"
    mock_repo.update_leave_status.assert_called_once_with(1, LeaveStatus.APPROVED)
    mock_repo.update_employee_remaining_days.assert_called_once_with(100, 2)

def test_execute_insufficient_days():
    # 1. Setup mocks
    mock_repo = MagicMock()
    mock_domain_service = MagicMock()

    mock_leave_request = MagicMock()
    mock_leave_request.status = LeaveStatus.PENDING
    mock_repo.get_leave_request.return_value = mock_leave_request
    mock_repo.get_employee.return_value = MagicMock()
    
    # 2. Domain rule trả về False (Không đủ ngày phép)
    mock_domain_service.can_approve_leave.return_value = False

    usecase = ApproveLeaveUseCase(repo=mock_repo, domain_service=mock_domain_service)
    
    # 3. Act
    result = usecase.execute(1)

    # 4. Assert
    assert result["success"] is False
    assert result["message"] == "Nhân viên không đủ ngày nghỉ phép."
    # Xác nhận DB KHÔNG bị thay đổi
    mock_repo.update_leave_status.assert_not_called()

def test_execute_leave_not_found():
    mock_repo = MagicMock()
    mock_domain_service = MagicMock()
    
    mock_repo.get_leave_request.return_value = None
    usecase = ApproveLeaveUseCase(repo=mock_repo, domain_service=mock_domain_service)
    
    result = usecase.execute(1)
    assert result["success"] is False
    assert result["message"] == "Không tìm thấy đơn."
    mock_repo.update_leave_status.assert_not_called()

def test_execute_already_processed():
    mock_repo = MagicMock()
    mock_domain_service = MagicMock()
    
    mock_leave_request = MagicMock()
    mock_leave_request.status = LeaveStatus.APPROVED
    mock_repo.get_leave_request.return_value = mock_leave_request
    
    usecase = ApproveLeaveUseCase(repo=mock_repo, domain_service=mock_domain_service)
    
    result = usecase.execute(1)
    assert result["success"] is False
    assert result["message"] == "Đơn đã được xử lý."
    mock_repo.update_leave_status.assert_not_called()
