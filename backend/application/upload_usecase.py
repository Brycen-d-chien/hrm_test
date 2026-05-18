from backend.domain.s3_service import S3DomainService
from backend.domain.storage_entity import S3StorageError, S3ValidationError
from backend.infrastructure.s3_repository import S3Repository


class UploadEmployeeDocumentUseCase:
    # Level 2: validate -> build key -> upload to storage.

    def __init__(self, repo: S3Repository, domain_service: S3DomainService):
        self.repo = repo
        self.domain_service = domain_service

    def execute(
        self,
        employee_id: int,
        folder: str,
        filename: str,
        data: bytes,
        content_type: str,
    ) -> dict:
        size = len(data)

        try:
            self.domain_service.validate_upload(
                employee_id, folder, filename, size, content_type
            )
        except S3ValidationError as error:
            return {"success": False, "message": str(error), "status_code": 400}

        key = self.domain_service.build_object_key(employee_id, folder, filename)

        try:
            self.repo.put_object_bytes(
                key, data, content_type, metadata={"employee_id": str(employee_id)}
            )
        except S3StorageError as error:
            return {
                "success": False,
                "message": f"Loi luu tru: {error}",
                "status_code": 502,
            }

        return {
            "success": True,
            "key": key,
            "bucket": self.repo.bucket,
            "size": size,
            "content_type": content_type,
        }
