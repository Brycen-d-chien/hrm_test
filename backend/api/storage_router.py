from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from backend.application.download_usecase import GenerateDownloadUrlUseCase
from backend.application.manage_objects_usecase import (
    DeleteObjectUseCase,
    ListFolderObjectsUseCase,
)
from backend.application.upload_usecase import UploadEmployeeDocumentUseCase
from backend.domain.s3_service import MAX_FILE_SIZE_BYTES, S3DomainService
from backend.infrastructure.auth import get_current_user, require_admin
from backend.infrastructure.s3_config import get_s3_bucket, get_s3_client
from backend.infrastructure.s3_repository import S3Repository
from backend.infrastructure.s3_utils import detect_content_type

router = APIRouter(prefix="/api/storage", tags=["Storage"])

_READ_CHUNK_SIZE = 1024 * 1024


def get_s3_repository():
    return S3Repository(client=get_s3_client(), bucket=get_s3_bucket())


def get_s3_domain_service():
    return S3DomainService()


def get_upload_usecase(
    repo: S3Repository = Depends(get_s3_repository),
    domain_service: S3DomainService = Depends(get_s3_domain_service),
) -> UploadEmployeeDocumentUseCase:
    return UploadEmployeeDocumentUseCase(repo, domain_service)


def get_download_url_usecase(
    repo: S3Repository = Depends(get_s3_repository),
    domain_service: S3DomainService = Depends(get_s3_domain_service),
) -> GenerateDownloadUrlUseCase:
    return GenerateDownloadUrlUseCase(repo, domain_service)


def get_delete_usecase(
    repo: S3Repository = Depends(get_s3_repository),
    domain_service: S3DomainService = Depends(get_s3_domain_service),
) -> DeleteObjectUseCase:
    return DeleteObjectUseCase(repo, domain_service)


def get_list_folder_usecase(
    repo: S3Repository = Depends(get_s3_repository),
    domain_service: S3DomainService = Depends(get_s3_domain_service),
) -> ListFolderObjectsUseCase:
    return ListFolderObjectsUseCase(repo, domain_service)


async def _read_upload_bytes(file: UploadFile, max_bytes: int) -> bytes:
    data = bytearray()
    while True:
        chunk = await file.read(_READ_CHUNK_SIZE)
        if not chunk:
            break

        remaining = max_bytes - len(data)
        if remaining <= 0:
            break

        data.extend(chunk[:remaining])
        if len(data) >= max_bytes:
            break

    return bytes(data)


def _raise_for_failure(result: dict, default_status_code: int) -> None:
    if result["success"]:
        return

    raise HTTPException(
        status_code=result.get("status_code", default_status_code),
        detail=result["message"],
    )


def _ensure_employee_can_access_key(
    current_user: dict, key: str, domain_service: S3DomainService
) -> None:
    if current_user["role"] == "Admin":
        return

    if not domain_service.is_object_owned_by_employee(current_user["id"], key):
        raise HTTPException(status_code=403, detail="Ban khong co quyen truy cap object nay.")


def _ensure_employee_can_access_employee(
    current_user: dict, employee_id: int
) -> None:
    if current_user["role"] == "Admin":
        return

    if current_user["id"] != employee_id:
        raise HTTPException(status_code=403, detail="Ban khong co quyen xem objects cua employee nay.")


@router.post("/upload")
async def upload_file(
    employee_id: int = Form(...),
    folder: str = Form(...),
    file: UploadFile = File(...),
    usecase: UploadEmployeeDocumentUseCase = Depends(get_upload_usecase),
    admin_user: dict = Depends(require_admin),
):
    data = await _read_upload_bytes(file, MAX_FILE_SIZE_BYTES + 1)
    content_type = file.content_type or detect_content_type(file.filename or "")
    result = usecase.execute(
        employee_id=employee_id,
        folder=folder,
        filename=file.filename or "upload",
        data=data,
        content_type=content_type,
    )
    _raise_for_failure(result, 400)
    return result


@router.get("/download-url")
def get_download_url(
    key: str,
    expires_in: int = 3600,
    usecase: GenerateDownloadUrlUseCase = Depends(get_download_url_usecase),
    domain_service: S3DomainService = Depends(get_s3_domain_service),
    current_user: dict = Depends(get_current_user),
):
    _ensure_employee_can_access_key(current_user, key, domain_service)

    result = usecase.execute(key=key, expires_in=expires_in)
    _raise_for_failure(result, 404)
    return result


@router.get("/objects")
def list_objects(
    employee_id: int,
    folder: str,
    usecase: ListFolderObjectsUseCase = Depends(get_list_folder_usecase),
    current_user: dict = Depends(get_current_user),
):
    _ensure_employee_can_access_employee(current_user, employee_id)

    result = usecase.execute(employee_id=employee_id, folder=folder)
    _raise_for_failure(result, 400)
    return result


@router.delete("/object")
def delete_object(
    key: str,
    usecase: DeleteObjectUseCase = Depends(get_delete_usecase),
    admin_user: dict = Depends(require_admin),
):
    result = usecase.execute(key=key)
    _raise_for_failure(result, 404)
    return result
