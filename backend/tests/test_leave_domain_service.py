import pytest
from unittest.mock import MagicMock
from backend.domain.leave_service import LeaveDomainService


def make_employee(remaining_days: int):
    emp = MagicMock()
    emp.remaining_leave_days = remaining_days
    return emp


class TestCanApproveLeave:
    def setup_method(self):
        self.service = LeaveDomainService()

    def test_returns_true_when_enough_days(self):
        emp = make_employee(remaining_days=5)
        assert self.service.can_approve_leave(emp, 5) is True

    def test_returns_true_when_more_than_enough_days(self):
        emp = make_employee(remaining_days=10)
        assert self.service.can_approve_leave(emp, 3) is True

    def test_returns_false_when_not_enough_days(self):
        emp = make_employee(remaining_days=1)
        assert self.service.can_approve_leave(emp, 5) is False

    def test_returns_false_when_zero_remaining_days(self):
        emp = make_employee(remaining_days=0)
        assert self.service.can_approve_leave(emp, 1) is False

    def test_returns_false_when_requested_days_is_zero(self):
        emp = make_employee(remaining_days=10)
        assert self.service.can_approve_leave(emp, 0) is False

    def test_returns_false_when_requested_days_is_negative(self):
        emp = make_employee(remaining_days=10)
        assert self.service.can_approve_leave(emp, -1) is False
