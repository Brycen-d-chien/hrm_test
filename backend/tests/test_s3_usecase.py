import pytest
from unittest.mock import MagicMock
from datetime import datetime, timezone

from backend.application.upload_usecase import UploadEmployeeDocumentUseCase
from backend.application.download_usecase import GenerateDownloadUrlUseCase
from backend.application.manage_objects_usecase import DeleteObjectUseCase, ListFolderObjectsUseCase
from backend.domain.storage_entity import S3ValidationError, S3StorageError


def make_mocks():
    mock_repo = MagicMock()
    mock_repo.bucket = "test-bucket"
    mock_domain_service = MagicMock()
    return mock_repo, mock_domain_service


class TestUploadEmployeeDocumentUseCase:
    def test_execute_success(self):
        mock_repo, mock_ds = make_mocks()
        mock_ds.validate_upload.return_value = None
        mock_ds.build_object_key.return_value = "avatars/employee_1/photo.jpg"

        usecase = UploadEmployeeDocumentUseCase(mock_repo, mock_ds)
        result = usecase.execute(1, "avatars", "photo.jpg", b"data", "image/jpeg")

        assert result["success"] is True
        assert result["key"] == "avatars/employee_1/photo.jpg"
        assert result["bucket"] == "test-bucket"
        mock_repo.put_object_bytes.assert_called_once()

    def test_execute_returns_failure_on_validation_error(self):
        mock_repo, mock_ds = make_mocks()
        mock_ds.validate_upload.side_effect = S3ValidationError("File quá lớn.")

        usecase = UploadEmployeeDocumentUseCase(mock_repo, mock_ds)
        result = usecase.execute(1, "avatars", "photo.jpg", b"data", "image/jpeg")

        assert result["success"] is False
        assert "quá lớn" in result["message"]
        mock_repo.put_object_bytes.assert_not_called()

    def test_execute_returns_failure_on_storage_error(self):
        mock_repo, mock_ds = make_mocks()
        mock_ds.validate_upload.return_value = None
        mock_ds.build_object_key.return_value = "avatars/employee_1/photo.jpg"
        mock_repo.put_object_bytes.side_effect = S3StorageError("S3 unreachable")

        usecase = UploadEmployeeDocumentUseCase(mock_repo, mock_ds)
        result = usecase.execute(1, "avatars", "photo.jpg", b"data", "image/jpeg")

        assert result["success"] is False
        assert "Lỗi lưu trữ" in result["message"]


class TestGenerateDownloadUrlUseCase:
    def test_execute_success(self):
        mock_repo, mock_ds = make_mocks()
        mock_repo.object_exists.return_value = True
        mock_repo.generate_presigned_url.return_value = "https://s3.example.com/signed"

        usecase = GenerateDownloadUrlUseCase(mock_repo, mock_ds)
        result = usecase.execute("avatars/employee_1/photo.jpg")

        assert result["success"] is True
        assert result["url"] == "https://s3.example.com/signed"

    def test_execute_returns_failure_when_object_missing(self):
        mock_repo, mock_ds = make_mocks()
        mock_repo.object_exists.return_value = False

        usecase = GenerateDownloadUrlUseCase(mock_repo, mock_ds)
        result = usecase.execute("avatars/employee_1/photo.jpg")

        assert result["success"] is False
        assert "không tồn tại" in result["message"]
        mock_repo.generate_presigned_url.assert_not_called()

    def test_execute_returns_failure_on_storage_error(self):
        mock_repo, mock_ds = make_mocks()
        mock_repo.object_exists.return_value = True
        mock_repo.generate_presigned_url.side_effect = S3StorageError("Signing failed")

        usecase = GenerateDownloadUrlUseCase(mock_repo, mock_ds)
        result = usecase.execute("some/key")

        assert result["success"] is False
        assert "Không thể tạo URL" in result["message"]


class TestDeleteObjectUseCase:
    def test_execute_success(self):
        mock_repo, mock_ds = make_mocks()
        mock_repo.object_exists.return_value = True

        usecase = DeleteObjectUseCase(mock_repo, mock_ds)
        result = usecase.execute("some/key")

        assert result["success"] is True
        mock_repo.delete_object.assert_called_once_with("some/key")

    def test_execute_returns_failure_when_object_missing(self):
        mock_repo, mock_ds = make_mocks()
        mock_repo.object_exists.return_value = False

        usecase = DeleteObjectUseCase(mock_repo, mock_ds)
        result = usecase.execute("missing/key")

        assert result["success"] is False
        mock_repo.delete_object.assert_not_called()

    def test_execute_returns_failure_on_storage_error(self):
        mock_repo, mock_ds = make_mocks()
        mock_repo.object_exists.return_value = True
        mock_repo.delete_object.side_effect = S3StorageError("Delete failed")

        usecase = DeleteObjectUseCase(mock_repo, mock_ds)
        result = usecase.execute("some/key")

        assert result["success"] is False
        assert "Lỗi xóa" in result["message"]


class TestListFolderObjectsUseCase:
    def test_execute_success_returns_objects(self):
        mock_repo, mock_ds = make_mocks()
        mock_ds.build_folder_prefix.return_value = "documents/employee_1/"
        mock_repo.list_objects.return_value = [
            {"Key": "documents/employee_1/file.pdf", "Size": 1024, "LastModified": datetime(2026, 1, 1, tzinfo=timezone.utc)},
        ]

        usecase = ListFolderObjectsUseCase(mock_repo, mock_ds)
        result = usecase.execute(1, "documents")

        assert result["success"] is True
        assert result["count"] == 1
        assert result["objects"][0]["key"] == "documents/employee_1/file.pdf"

    def test_execute_returns_empty_list_when_no_objects(self):
        mock_repo, mock_ds = make_mocks()
        mock_ds.build_folder_prefix.return_value = "avatars/employee_99/"
        mock_repo.list_objects.return_value = []

        usecase = ListFolderObjectsUseCase(mock_repo, mock_ds)
        result = usecase.execute(99, "avatars")

        assert result["success"] is True
        assert result["count"] == 0
        assert result["objects"] == []

    def test_execute_returns_failure_on_storage_error(self):
        mock_repo, mock_ds = make_mocks()
        mock_ds.build_folder_prefix.return_value = "documents/employee_1/"
        mock_repo.list_objects.side_effect = S3StorageError("ListObjects failed")

        usecase = ListFolderObjectsUseCase(mock_repo, mock_ds)
        result = usecase.execute(1, "documents")

        assert result["success"] is False
        assert "Lỗi liệt kê" in result["message"]
