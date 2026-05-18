from backend.infrastructure.s3_repository import S3Repository
from backend.domain.s3_service import S3DomainService
from backend.domain.storage_entity import S3ValidationError, S3StorageError


class UploadEmployeeDocumentUseCase:
    # Cấp 2: Orchestrate upload - validate -> build key -> put object

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
            self.domain_service.validate_upload(employee_id, folder, filename, size, content_type)
        except S3ValidationError as e:
            return {"success": False, "message": str(e)}

        key = self.domain_service.build_object_key(employee_id, folder, filename)

        try:
            self.repo.put_object_bytes(
                key, data, content_type, metadata={"employee_id": str(employee_id)}
            )
        except S3StorageError as e:
            return {"success": False, "message": f"Lỗi lưu trữ: {e}"}

        return {
            "success": True,
            "key": key,
            "bucket": self.repo.bucket,
            "size": size,
            "content_type": content_type,
        }
