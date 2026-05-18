from pydantic import BaseModel
from datetime import datetime


# --- Custom Exceptions ---

class S3StorageError(Exception):
    """Lỗi chung khi tương tác với S3."""


class S3ObjectNotFoundError(S3StorageError):
    """Object không tồn tại trong S3."""


class S3PermissionError(S3StorageError):
    """Không có quyền truy cập S3."""


class S3ValidationError(Exception):
    """Dữ liệu đầu vào vi phạm business rule của storage."""


# --- Pydantic Schemas ---

class S3UploadResult(BaseModel):
    key: str
    bucket: str
    size: int
    content_type: str


class S3ObjectInfo(BaseModel):
    key: str
    size: int
    last_modified: datetime
