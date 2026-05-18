import re

from backend.domain.storage_entity import S3ValidationError

ALLOWED_FOLDERS = {"avatars", "documents", "leave-attachments"}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB

_SAFE_FILENAME_RE = re.compile(r"^[\w\-. ]+$")


class S3DomainService:
    # Cấp 3: Business rule cho storage - folder, size, naming convention

    def validate_upload(
        self, employee_id: int, folder: str, filename: str, size: int, content_type: str
    ) -> None:
        if folder not in ALLOWED_FOLDERS:
            raise S3ValidationError(
                f"Folder '{folder}' không được phép. Chỉ chấp nhận: {sorted(ALLOWED_FOLDERS)}"
            )
        if size <= 0:
            raise S3ValidationError("File không được rỗng.")
        if size > MAX_FILE_SIZE_BYTES:
            raise S3ValidationError(
                f"File vượt quá giới hạn {MAX_FILE_SIZE_BYTES // (1024 * 1024)} MB."
            )
        if not filename or not _SAFE_FILENAME_RE.match(filename):
            raise S3ValidationError(
                "Tên file chứa ký tự không hợp lệ. Chỉ chấp nhận chữ, số, dấu '-', '_', '.'."
            )

    def build_object_key(self, employee_id: int, folder: str, filename: str) -> str:
        """Tạo S3 key theo pattern: {folder}/employee_{id}/{filename}"""
        safe_name = filename.strip().replace(" ", "_")
        return f"{folder}/employee_{employee_id}/{safe_name}"

    def build_folder_prefix(self, employee_id: int, folder: str) -> str:
        """Prefix để list toàn bộ file của employee trong một folder."""
        return f"{folder}/employee_{employee_id}/"
