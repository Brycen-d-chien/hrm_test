import pytest
from unittest.mock import MagicMock
from botocore.exceptions import ClientError

from backend.infrastructure.s3_repository import S3Repository
from backend.domain.storage_entity import S3ObjectNotFoundError, S3PermissionError, S3StorageError


def make_client_error(code: str) -> ClientError:
    return ClientError({"Error": {"Code": code, "Message": "test error"}}, "TestOperation")


def make_repo() -> tuple[MagicMock, S3Repository]:
    mock_client = MagicMock()
    repo = S3Repository(client=mock_client, bucket="test-bucket")
    return mock_client, repo


class TestPutObjectBytes:
    def test_calls_put_object_with_correct_params(self):
        mock_client, repo = make_repo()
        repo.put_object_bytes("avatars/employee_1/photo.jpg", b"data", "image/jpeg")
        mock_client.put_object.assert_called_once_with(
            Bucket="test-bucket",
            Key="avatars/employee_1/photo.jpg",
            Body=b"data",
            ContentType="image/jpeg",
        )

    def test_passes_metadata_when_provided(self):
        mock_client, repo = make_repo()
        repo.put_object_bytes("key", b"data", "text/plain", metadata={"employee_id": "1"})
        call_kwargs = mock_client.put_object.call_args[1]
        assert call_kwargs["Metadata"] == {"employee_id": "1"}

    def test_raises_s3_storage_error_on_internal_error(self):
        mock_client, repo = make_repo()
        mock_client.put_object.side_effect = make_client_error("InternalError")
        with pytest.raises(S3StorageError):
            repo.put_object_bytes("key", b"data", "text/plain")

    def test_raises_s3_permission_error_on_403(self):
        mock_client, repo = make_repo()
        mock_client.put_object.side_effect = make_client_error("AccessDenied")
        with pytest.raises(S3PermissionError):
            repo.put_object_bytes("key", b"data", "text/plain")


class TestGetObjectBytes:
    def test_returns_bytes_from_body(self):
        mock_client, repo = make_repo()
        mock_client.get_object.return_value = {"Body": MagicMock(read=lambda: b"file content")}
        result = repo.get_object_bytes("some/key")
        assert result == b"file content"

    def test_raises_s3_object_not_found_on_404(self):
        mock_client, repo = make_repo()
        mock_client.get_object.side_effect = make_client_error("NoSuchKey")
        with pytest.raises(S3ObjectNotFoundError):
            repo.get_object_bytes("missing/key")


class TestDeleteObject:
    def test_calls_delete_object(self):
        mock_client, repo = make_repo()
        repo.delete_object("some/key")
        mock_client.delete_object.assert_called_once_with(Bucket="test-bucket", Key="some/key")

    def test_raises_s3_storage_error_on_failure(self):
        mock_client, repo = make_repo()
        mock_client.delete_object.side_effect = make_client_error("InternalError")
        with pytest.raises(S3StorageError):
            repo.delete_object("some/key")


class TestListObjects:
    def test_returns_contents_list(self):
        mock_client, repo = make_repo()
        mock_client.list_objects_v2.return_value = {"Contents": [{"Key": "a"}, {"Key": "b"}]}
        result = repo.list_objects("prefix/")
        assert len(result) == 2

    def test_returns_empty_list_when_no_contents(self):
        mock_client, repo = make_repo()
        mock_client.list_objects_v2.return_value = {}
        result = repo.list_objects("prefix/")
        assert result == []


class TestGeneratePresignedUrl:
    def test_returns_url_string(self):
        mock_client, repo = make_repo()
        mock_client.generate_presigned_url.return_value = "https://s3.example.com/signed"
        url = repo.generate_presigned_url("some/key", expires_in=300)
        assert url == "https://s3.example.com/signed"
        mock_client.generate_presigned_url.assert_called_once_with(
            "get_object",
            Params={"Bucket": "test-bucket", "Key": "some/key"},
            ExpiresIn=300,
        )


class TestObjectExists:
    def test_returns_true_when_head_object_succeeds(self):
        mock_client, repo = make_repo()
        mock_client.head_object.return_value = {}
        assert repo.object_exists("some/key") is True

    def test_returns_false_on_404(self):
        mock_client, repo = make_repo()
        mock_client.head_object.side_effect = make_client_error("404")
        assert repo.object_exists("missing/key") is False

    def test_raises_s3_permission_error_on_403(self):
        mock_client, repo = make_repo()
        mock_client.head_object.side_effect = make_client_error("AccessDenied")
        with pytest.raises(S3PermissionError):
            repo.object_exists("some/key")
