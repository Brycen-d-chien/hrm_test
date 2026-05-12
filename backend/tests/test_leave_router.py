import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock

from backend.main import app
from backend.infrastructure.database import get_db
from backend.infrastructure.auth import require_admin
from backend.api.leave_router import get_approve_leave_usecase


# --- Test POST /api/leaves/{leave_id}/approve ---

class TestApproveLeaveRouter:
    def test_approve_success_returns_200(self):
        mock_usecase = MagicMock()
        mock_usecase.execute.return_value = {"success": True, "message": "Duyệt thành công!"}

        app.dependency_overrides[get_approve_leave_usecase] = lambda: mock_usecase
        app.dependency_overrides[require_admin] = lambda: {"id": 1, "role": "Admin"}

        client = TestClient(app)
        response = client.post("/api/leaves/1/approve")

        assert response.status_code == 200
        assert response.json()["success"] is True
        assert response.json()["message"] == "Duyệt thành công!"
        mock_usecase.execute.assert_called_once_with(1)

        app.dependency_overrides.clear()

    def test_approve_returns_400_when_usecase_fails(self):
        mock_usecase = MagicMock()
        mock_usecase.execute.return_value = {"success": False, "message": "Nhân viên không đủ ngày nghỉ phép."}

        app.dependency_overrides[get_approve_leave_usecase] = lambda: mock_usecase
        app.dependency_overrides[require_admin] = lambda: {"id": 1, "role": "Admin"}

        client = TestClient(app)
        response = client.post("/api/leaves/1/approve")

        assert response.status_code == 400
        assert response.json()["detail"] == "Nhân viên không đủ ngày nghỉ phép."

        app.dependency_overrides.clear()

    def test_approve_returns_400_when_leave_not_found(self):
        mock_usecase = MagicMock()
        mock_usecase.execute.return_value = {"success": False, "message": "Không tìm thấy đơn."}

        app.dependency_overrides[get_approve_leave_usecase] = lambda: mock_usecase
        app.dependency_overrides[require_admin] = lambda: {"id": 1, "role": "Admin"}

        client = TestClient(app)
        response = client.post("/api/leaves/999/approve")

        assert response.status_code == 400
        assert response.json()["detail"] == "Không tìm thấy đơn."

        app.dependency_overrides.clear()

    def test_approve_returns_403_when_not_admin(self):
        # Không override require_admin → 403
        mock_db = MagicMock()
        app.dependency_overrides[get_db] = lambda: mock_db

        client = TestClient(app)
        response = client.post(
            "/api/leaves/1/approve",
            headers={"x-user-role": "Employee", "x-user-id": "2"}
        )

        assert response.status_code == 403

        app.dependency_overrides.clear()
