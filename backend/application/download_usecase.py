from backend.infrastructure.s3_repository import S3Repository
from backend.domain.s3_service import S3DomainService
from backend.domain.storage_entity import S3StorageError


class GenerateDownloadUrlUseCase:
    # Cấp 2: Kiểm tra object tồn tại rồi tạo presigned URL

    def __init__(self, repo: S3Repository, domain_service: S3DomainService):
        self.repo = repo
        self.domain_service = domain_service

    def execute(self, key: str, expires_in: int = 3600) -> dict:
        if not self.repo.object_exists(key):
            return {"success": False, "message": "Object không tồn tại."}

        try:
            url = self.repo.generate_presigned_url(key, expires_in)
        except S3StorageError as e:
            return {"success": False, "message": f"Không thể tạo URL: {e}"}

        return {"success": True, "url": url, "expires_in": expires_in}
