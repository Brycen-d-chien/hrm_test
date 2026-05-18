import re

from backend.domain.storage_entity import S3ValidationError

ALLOWED_FOLDERS = {"avatars", "documents", "leave-attachments"}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB

_SAFE_FILENAME_RE = re.compile(r"^[\w\-. ]+$")
_OBJECT_KEY_RE = re.compile(r"^(?P<folder>[\w-]+)/employee_(?P<employee_id>\d+)/.+$")


class S3DomainService:
    # Level 3: storage business rules for folder, size, naming, and ownership.

    def validate_folder(self, folder: str) -> None:
        if folder not in ALLOWED_FOLDERS:
            raise S3ValidationError(
                f"Folder '{folder}' khong duoc phep. Chap nhan: {sorted(ALLOWED_FOLDERS)}"
            )

    def validate_upload(
        self, employee_id: int, folder: str, filename: str, size: int, content_type: str
    ) -> None:
        self.validate_folder(folder)

        if size <= 0:
            raise S3ValidationError("File khong duoc rong.")
        if size > MAX_FILE_SIZE_BYTES:
            raise S3ValidationError(
                f"File vuot qua gioi han {MAX_FILE_SIZE_BYTES // (1024 * 1024)} MB."
            )
        if not filename or not _SAFE_FILENAME_RE.match(filename):
            raise S3ValidationError(
                "Ten file chua ky tu khong hop le. Chi chap nhan chu, so, dau '-', '_', '.'."
            )

    def build_object_key(self, employee_id: int, folder: str, filename: str) -> str:
        safe_name = filename.strip().replace(" ", "_")
        return f"{folder}/employee_{employee_id}/{safe_name}"

    def build_folder_prefix(self, employee_id: int, folder: str) -> str:
        self.validate_folder(folder)
        return f"{folder}/employee_{employee_id}/"

    def is_object_owned_by_employee(self, employee_id: int, key: str) -> bool:
        match = _OBJECT_KEY_RE.match(key.strip())
        if not match:
            return False

        folder = match.group("folder")
        return folder in ALLOWED_FOLDERS and int(match.group("employee_id")) == employee_id
