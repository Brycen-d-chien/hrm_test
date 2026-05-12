import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session

from backend.main import app
from backend.infrastructure.database import get_db
from backend.infrastructure.auth import get_current_user, require_admin
from backend.domain.leave_entity import EmployeeModel

# --- Helpers ---

def make_employee(id=1, name="Nguyen Van A", role="Employee", remaining_leave_days=12):
    emp = MagicMock(spec=EmployeeModel)
    emp.id = id
    emp.name = name
    emp.role = role
    emp.remaining_leave_days = remaining_leave_days
    return emp


def admin_user():
    return {"id": 1, "role": "Admin"}


def normal_user(user_id=2):
    return {"id": user_id, "role": "Employee"}


# --- Test GET /api/employees/ ---

class TestGetEmployees:
    def test_admin_can_list_employees(self):
        mock_db = MagicMock(spec=Session)
        employees = [make_employee(1), make_employee(2, name="Tran Thi B")]
        mock_db.query.return_value.all.return_value = employees

        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[require_admin] = lambda: admin_user()

        client = TestClient(app)
        response = client.get("/api/employees/")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == "Nguyen Van A"

        app.dependency_overrides.clear()

    def test_non_admin_cannot_list_employees(self):
        # Không override require_admin → FastAPI raise 403
        mock_db = MagicMock(spec=Session)
        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_current_user] = lambda: normal_user()

        client = TestClient(app)
        response = client.get("/api/employees/", headers={"x-user-role": "Employee", "x-user-id": "2"})

        assert response.status_code == 403

        app.dependency_overrides.clear()


# --- Test GET /api/employees/me ---

class TestGetMyInfo:
    def test_returns_own_employee_info(self):
        user_id = 5
        mock_db = MagicMock(spec=Session)
        emp = make_employee(id=user_id, name="Le Van C")
        mock_db.query.return_value.filter.return_value.first.return_value = emp

        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_current_user] = lambda: {"id": user_id, "role": "Employee"}

        client = TestClient(app)
        response = client.get("/api/employees/me")

        assert response.status_code == 200
        assert response.json()["name"] == "Le Van C"

        app.dependency_overrides.clear()

    def test_returns_404_when_employee_not_found(self):
        user_id = 99
        mock_db = MagicMock(spec=Session)
        mock_db.query.return_value.filter.return_value.first.return_value = None

        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_current_user] = lambda: {"id": user_id, "role": "Employee"}

        client = TestClient(app)
        response = client.get("/api/employees/me")

        assert response.status_code == 404
        assert "Không tìm thấy" in response.json()["detail"]

        app.dependency_overrides.clear()


# --- Test POST /api/employees/ ---

class TestCreateEmployee:
    def test_admin_can_create_employee(self):
        mock_db = MagicMock(spec=Session)
        created_emp = make_employee(id=10, name="Pham Van D", role="Employee", remaining_leave_days=14)

        # db.refresh sẽ populate emp được add
        def fake_refresh(obj):
            obj.id = created_emp.id
            obj.name = created_emp.name
            obj.role = created_emp.role
            obj.remaining_leave_days = created_emp.remaining_leave_days

        mock_db.refresh.side_effect = fake_refresh

        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[require_admin] = lambda: admin_user()

        client = TestClient(app)
        response = client.post("/api/employees/", json={
            "name": "Pham Van D",
            "role": "Employee",
            "remaining_leave_days": 14
        })

        assert response.status_code == 201
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

        app.dependency_overrides.clear()

    def test_non_admin_cannot_create_employee(self):
        mock_db = MagicMock(spec=Session)
        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_current_user] = lambda: normal_user()

        client = TestClient(app)
        response = client.post("/api/employees/", json={
            "name": "Hacker",
            "role": "Employee",
            "remaining_leave_days": 0
        }, headers={"x-user-role": "Employee", "x-user-id": "2"})

        assert response.status_code == 403

        app.dependency_overrides.clear()
