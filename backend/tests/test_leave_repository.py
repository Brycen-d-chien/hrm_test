import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from backend.infrastructure.leave_repository import LeaveRepository
from backend.domain.leave_entity import LeaveStatus


def make_db_session():
    return MagicMock()


class TestGetLeaveRequest:
    def test_returns_leave_request_when_found(self):
        db = make_db_session()
        mock_request = MagicMock()
        mock_request.id = 1
        db.query.return_value.filter.return_value.first.return_value = mock_request

        repo = LeaveRepository(db)
        result = repo.get_leave_request(1)

        assert result == mock_request
        db.query.assert_called_once()

    def test_returns_none_when_not_found(self):
        db = make_db_session()
        db.query.return_value.filter.return_value.first.return_value = None

        repo = LeaveRepository(db)
        result = repo.get_leave_request(999)

        assert result is None


class TestGetEmployee:
    def test_returns_employee_when_found(self):
        db = make_db_session()
        mock_emp = MagicMock()
        mock_emp.id = 100
        db.query.return_value.filter.return_value.first.return_value = mock_emp

        repo = LeaveRepository(db)
        result = repo.get_employee(100)

        assert result == mock_emp

    def test_returns_none_when_not_found(self):
        db = make_db_session()
        db.query.return_value.filter.return_value.first.return_value = None

        repo = LeaveRepository(db)
        result = repo.get_employee(999)

        assert result is None


class TestUpdateLeaveStatus:
    def test_updates_status_when_request_exists(self):
        db = make_db_session()
        mock_request = MagicMock()
        mock_request.id = 1
        mock_request.status = LeaveStatus.PENDING
        db.query.return_value.filter.return_value.first.return_value = mock_request

        repo = LeaveRepository(db)
        repo.update_leave_status(1, LeaveStatus.APPROVED)

        assert mock_request.status == LeaveStatus.APPROVED
        db.commit.assert_called_once()

    def test_does_nothing_when_request_not_found(self):
        db = make_db_session()
        db.query.return_value.filter.return_value.first.return_value = None

        repo = LeaveRepository(db)
        repo.update_leave_status(999, LeaveStatus.APPROVED)

        db.commit.assert_not_called()


class TestUpdateEmployeeRemainingDays:
    def test_deducts_days_when_employee_exists(self):
        db = make_db_session()
        mock_emp = MagicMock()
        mock_emp.remaining_leave_days = 10
        db.query.return_value.filter.return_value.first.return_value = mock_emp

        repo = LeaveRepository(db)
        repo.update_employee_remaining_days(100, 3)

        assert mock_emp.remaining_leave_days == 7
        db.commit.assert_called_once()

    def test_does_nothing_when_employee_not_found(self):
        db = make_db_session()
        db.query.return_value.filter.return_value.first.return_value = None

        repo = LeaveRepository(db)
        repo.update_employee_remaining_days(999, 3)

        db.commit.assert_not_called()
