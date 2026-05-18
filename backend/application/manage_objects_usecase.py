from backend.infrastructure.s3_repository import S3Repository
from backend.domain.s3_service import S3DomainService
from backend.domain.storage_entity import S3StorageError


class DeleteObjectUseCase:
    # Cấp 2: Kiểm tra tồn tại rồi xóa object

    def __init__(self, repo: S3Repository, domain_service: S3DomainService):
        self.repo = repo
        self.domain_service = domain_service

    def execute(self, key: str) -> dict:
        if not self.repo.object_exists(key):
            return {"success": False, "message": "Object không tồn tại."}

        try:
            self.repo.delete_object(key)
        except S3StorageError as e:
            return {"success": False, "message": f"Lỗi xóa: {e}"}

        return {"success": True, "message": f"Đã xóa '{key}'."}


class ListFolderObjectsUseCase:
    # Cấp 2: List toàn bộ object trong folder của một employee

    def __init__(self, repo: S3Repository, domain_service: S3DomainService):
        self.repo = repo
        self.domain_service = domain_service

    def execute(self, employee_id: int, folder: str) -> dict:
        prefix = self.domain_service.build_folder_prefix(employee_id, folder)

        try:
            raw_objects = self.repo.list_objects(prefix)
        except S3StorageError as e:
            return {"success": False, "message": f"Lỗi liệt kê objects: {e}"}

        objects = [
            {
                "key": obj["Key"],
                "size": obj["Size"],
                "last_modified": obj["LastModified"].isoformat(),
            }
            for obj in raw_objects
        ]
        return {"success": True, "objects": objects, "count": len(objects)}
