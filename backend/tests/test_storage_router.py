import io
from unittest.mock import MagicMock

from fastapi import HTTPException
from fastapi.testclient import TestClient

from backend.api.storage_router import (
    get_delete_usecase,
    get_download_url_usecase,
    get_list_folder_usecase,
    get_upload_usecase,
)
from backend.infrastructure.auth import get_current_user, require_admin
from backend.main import app

ADMIN_USER = {"id": 1, "role": "Admin"}
EMPLOYEE_USER = {"id": 2, "role": "Employee"}


class TestUploadEndpoint:
    def test_upload_success_returns_200(self):
        mock_usecase = MagicMock()
        mock_usecase.execute.return_value = {
            "success": True,
            "key": "avatars/employee_1/photo.jpg",
            "bucket": "test-bucket",
            "size": 4,
            "content_type": "image/jpeg",
        }

        app.dependency_overrides[get_upload_usecase] = lambda: mock_usecase
        app.dependency_overrides[require_admin] = lambda: ADMIN_USER

        client = TestClient(app)
        response = client.post(
            "/api/storage/upload",
            data={"employee_id": 1, "folder": "avatars"},
            files={"file": ("photo.jpg", io.BytesIO(b"data"), "image/jpeg")},
        )

        assert response.status_code == 200
        assert response.json()["key"] == "avatars/employee_1/photo.jpg"
        app.dependency_overrides.clear()

    def test_upload_returns_400_on_validation_failure(self):
        mock_usecase = MagicMock()
        mock_usecase.execute.return_value = {
            "success": False,
            "message": "Folder khong duoc phep.",
            "status_code": 400,
        }

        app.dependency_overrides[get_upload_usecase] = lambda: mock_usecase
        app.dependency_overrides[require_admin] = lambda: ADMIN_USER

        client = TestClient(app)
        response = client.post(
            "/api/storage/upload",
            data={"employee_id": 1, "folder": "invoices"},
            files={"file": ("file.pdf", io.BytesIO(b"data"), "application/pdf")},
        )

        assert response.status_code == 400
        assert "Folder" in response.json()["detail"]
        app.dependency_overrides.clear()

    def test_upload_returns_502_on_storage_failure(self):
        mock_usecase = MagicMock()
        mock_usecase.execute.return_value = {
            "success": False,
            "message": "Loi luu tru: S3 down",
            "status_code": 502,
        }

        app.dependency_overrides[get_upload_usecase] = lambda: mock_usecase
        app.dependency_overrides[require_admin] = lambda: ADMIN_USER

        client = TestClient(app)
        response = client.post(
            "/api/storage/upload",
            data={"employee_id": 1, "folder": "avatars"},
            files={"file": ("photo.jpg", io.BytesIO(b"data"), "image/jpeg")},
        )

        assert response.status_code == 502
        app.dependency_overrides.clear()

    def test_upload_returns_403_when_not_admin(self):
        app.dependency_overrides[require_admin] = lambda: (_ for _ in ()).throw(
            HTTPException(status_code=403, detail="Admin only")
        )

        client = TestClient(app)
        response = client.post(
            "/api/storage/upload",
            data={"employee_id": 1, "folder": "avatars"},
            files={"file": ("photo.jpg", io.BytesIO(b"data"), "image/jpeg")},
        )

        assert response.status_code == 403
        app.dependency_overrides.clear()


class TestDownloadUrlEndpoint:
    def test_get_download_url_success(self):
        mock_usecase = MagicMock()
        mock_usecase.execute.return_value = {
            "success": True,
            "url": "https://s3.example.com/signed",
            "expires_in": 3600,
        }

        app.dependency_overrides[get_download_url_usecase] = lambda: mock_usecase
        app.dependency_overrides[get_current_user] = lambda: EMPLOYEE_USER

        client = TestClient(app)
        response = client.get(
            "/api/storage/download-url",
            params={"key": "avatars/employee_2/photo.jpg"},
        )

        assert response.status_code == 200
        assert response.json()["url"] == "https://s3.example.com/signed"
        app.dependency_overrides.clear()

    def test_get_download_url_returns_403_for_other_employee_key(self):
        mock_usecase = MagicMock()

        app.dependency_overrides[get_download_url_usecase] = lambda: mock_usecase
        app.dependency_overrides[get_current_user] = lambda: EMPLOYEE_USER

        client = TestClient(app)
        response = client.get(
            "/api/storage/download-url",
            params={"key": "avatars/employee_99/photo.jpg"},
        )

        assert response.status_code == 403
        mock_usecase.execute.assert_not_called()
        app.dependency_overrides.clear()

    def test_get_download_url_returns_404_when_missing(self):
        mock_usecase = MagicMock()
        mock_usecase.execute.return_value = {
            "success": False,
            "message": "Object khong ton tai.",
            "status_code": 404,
        }

        app.dependency_overrides[get_download_url_usecase] = lambda: mock_usecase
        app.dependency_overrides[get_current_user] = lambda: EMPLOYEE_USER

        client = TestClient(app)
        response = client.get(
            "/api/storage/download-url",
            params={"key": "avatars/employee_2/missing.jpg"},
        )

        assert response.status_code == 404
        app.dependency_overrides.clear()

    def test_get_download_url_returns_502_on_storage_failure(self):
        mock_usecase = MagicMock()
        mock_usecase.execute.return_value = {
            "success": False,
            "message": "Khong the tao URL: Signing failed",
            "status_code": 502,
        }

        app.dependency_overrides[get_download_url_usecase] = lambda: mock_usecase
        app.dependency_overrides[get_current_user] = lambda: EMPLOYEE_USER

        client = TestClient(app)
        response = client.get(
            "/api/storage/download-url",
            params={"key": "avatars/employee_2/photo.jpg"},
        )

        assert response.status_code == 502
        app.dependency_overrides.clear()


class TestListObjectsEndpoint:
    def test_list_objects_success(self):
        mock_usecase = MagicMock()
        mock_usecase.execute.return_value = {
            "success": True,
            "objects": [
                {
                    "key": "documents/employee_2/file.pdf",
                    "size": 1024,
                    "last_modified": "2026-01-01T00:00:00+00:00",
                }
            ],
            "count": 1,
        }

        app.dependency_overrides[get_list_folder_usecase] = lambda: mock_usecase
        app.dependency_overrides[get_current_user] = lambda: EMPLOYEE_USER

        client = TestClient(app)
        response = client.get(
            "/api/storage/objects",
            params={"employee_id": 2, "folder": "documents"},
        )

        assert response.status_code == 200
        assert response.json()["count"] == 1
        app.dependency_overrides.clear()

    def test_list_objects_returns_403_for_other_employee(self):
        mock_usecase = MagicMock()

        app.dependency_overrides[get_list_folder_usecase] = lambda: mock_usecase
        app.dependency_overrides[get_current_user] = lambda: EMPLOYEE_USER

        client = TestClient(app)
        response = client.get(
            "/api/storage/objects",
            params={"employee_id": 99, "folder": "documents"},
        )

        assert response.status_code == 403
        mock_usecase.execute.assert_not_called()
        app.dependency_overrides.clear()

    def test_list_objects_returns_400_for_invalid_folder(self):
        mock_usecase = MagicMock()
        mock_usecase.execute.return_value = {
            "success": False,
            "message": "Folder khong duoc phep.",
            "status_code": 400,
        }

        app.dependency_overrides[get_list_folder_usecase] = lambda: mock_usecase
        app.dependency_overrides[get_current_user] = lambda: EMPLOYEE_USER

        client = TestClient(app)
        response = client.get(
            "/api/storage/objects",
            params={"employee_id": 2, "folder": "invoices"},
        )

        assert response.status_code == 400
        app.dependency_overrides.clear()


class TestDeleteObjectEndpoint:
    def test_delete_success_returns_200(self):
        mock_usecase = MagicMock()
        mock_usecase.execute.return_value = {"success": True, "message": "Da xoa 'some/key'."}

        app.dependency_overrides[get_delete_usecase] = lambda: mock_usecase
        app.dependency_overrides[require_admin] = lambda: ADMIN_USER

        client = TestClient(app)
        response = client.delete("/api/storage/object", params={"key": "some/key"})

        assert response.status_code == 200
        assert response.json()["success"] is True
        app.dependency_overrides.clear()

    def test_delete_returns_404_when_object_missing(self):
        mock_usecase = MagicMock()
        mock_usecase.execute.return_value = {
            "success": False,
            "message": "Object khong ton tai.",
            "status_code": 404,
        }

        app.dependency_overrides[get_delete_usecase] = lambda: mock_usecase
        app.dependency_overrides[require_admin] = lambda: ADMIN_USER

        client = TestClient(app)
        response = client.delete("/api/storage/object", params={"key": "ghost/key"})

        assert response.status_code == 404
        app.dependency_overrides.clear()

    def test_delete_returns_502_on_storage_failure(self):
        mock_usecase = MagicMock()
        mock_usecase.execute.return_value = {
            "success": False,
            "message": "Loi xoa: Delete failed",
            "status_code": 502,
        }

        app.dependency_overrides[get_delete_usecase] = lambda: mock_usecase
        app.dependency_overrides[require_admin] = lambda: ADMIN_USER

        client = TestClient(app)
        response = client.delete("/api/storage/object", params={"key": "some/key"})

        assert response.status_code == 502
        app.dependency_overrides.clear()
