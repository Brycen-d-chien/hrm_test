from backend.domain.s3_service import S3DomainService
from backend.domain.storage_entity import S3StorageError, S3ValidationError
from backend.infrastructure.s3_repository import S3Repository


class DeleteObjectUseCase:
    # Level 2: check existence and delete object.

    def __init__(self, repo: S3Repository, domain_service: S3DomainService):
        self.repo = repo
        self.domain_service = domain_service

    def execute(self, key: str) -> dict:
        try:
            if not self.repo.object_exists(key):
                return {
                    "success": False,
                    "message": "Object khong ton tai.",
                    "status_code": 404,
                }

            self.repo.delete_object(key)
        except S3StorageError as error:
            return {
                "success": False,
                "message": f"Loi xoa: {error}",
                "status_code": 502,
            }

        return {"success": True, "message": f"Da xoa '{key}'."}


class ListFolderObjectsUseCase:
    # Level 2: list all objects in an employee folder.

    def __init__(self, repo: S3Repository, domain_service: S3DomainService):
        self.repo = repo
        self.domain_service = domain_service

    def execute(self, employee_id: int, folder: str) -> dict:
        try:
            prefix = self.domain_service.build_folder_prefix(employee_id, folder)
        except S3ValidationError as error:
            return {"success": False, "message": str(error), "status_code": 400}

        try:
            raw_objects = self.repo.list_objects(prefix)
        except S3StorageError as error:
            return {
                "success": False,
                "message": f"Loi liet ke objects: {error}",
                "status_code": 502,
            }

        objects = [
            {
                "key": obj["Key"],
                "size": obj["Size"],
                "last_modified": obj["LastModified"].isoformat(),
            }
            for obj in raw_objects
        ]
        return {"success": True, "objects": objects, "count": len(objects)}
