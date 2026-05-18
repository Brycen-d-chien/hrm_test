from backend.domain.s3_service import S3DomainService
from backend.domain.storage_entity import S3StorageError
from backend.infrastructure.s3_repository import S3Repository


class GenerateDownloadUrlUseCase:
    # Level 2: check existence and create a presigned URL.

    def __init__(self, repo: S3Repository, domain_service: S3DomainService):
        self.repo = repo
        self.domain_service = domain_service

    def execute(self, key: str, expires_in: int = 3600) -> dict:
        try:
            if not self.repo.object_exists(key):
                return {
                    "success": False,
                    "message": "Object khong ton tai.",
                    "status_code": 404,
                }

            url = self.repo.generate_presigned_url(key, expires_in)
        except S3StorageError as error:
            return {
                "success": False,
                "message": f"Khong the tao URL: {error}",
                "status_code": 502,
            }

        return {"success": True, "url": url, "expires_in": expires_in}
