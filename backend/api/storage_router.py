from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form

from backend.infrastructure.s3_config import get_s3_client, get_s3_bucket
from backend.infrastructure.s3_repository import S3Repository
from backend.infrastructure.s3_utils import detect_content_type
from backend.domain.s3_service import S3DomainService
from backend.application.upload_usecase import UploadEmployeeDocumentUseCase
from backend.application.download_usecase import GenerateDownloadUrlUseCase
from backend.application.manage_objects_usecase import DeleteObjectUseCase, ListFolderObjectsUseCase
from backend.infrastructure.auth import require_admin, get_current_user

router = APIRouter(prefix="/api/storage", tags=["Storage"])


# SOLID DI Dependencies Setup
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


# Cấp 1: Router nhận request
@router.post("/upload")
async def upload_file(
    employee_id: int = Form(...),
    folder: str = Form(...),
    file: UploadFile = File(...),
    usecase: UploadEmployeeDocumentUseCase = Depends(get_upload_usecase),
    admin_user: dict = Depends(require_admin),
):
    data = await file.read()
    content_type = file.content_type or detect_content_type(file.filename or "")
    result = usecase.execute(
        employee_id=employee_id,
        folder=folder,
        filename=file.filename or "upload",
        data=data,
        content_type=content_type,
    )
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@router.get("/download-url")
def get_download_url(
    key: str,
    expires_in: int = 3600,
    usecase: GenerateDownloadUrlUseCase = Depends(get_download_url_usecase),
    current_user: dict = Depends(get_current_user),
):
    result = usecase.execute(key=key, expires_in=expires_in)
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["message"])
    return result


@router.get("/objects")
def list_objects(
    employee_id: int,
    folder: str,
    usecase: ListFolderObjectsUseCase = Depends(get_list_folder_usecase),
    current_user: dict = Depends(get_current_user),
):
    result = usecase.execute(employee_id=employee_id, folder=folder)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@router.delete("/object")
def delete_object(
    key: str,
    usecase: DeleteObjectUseCase = Depends(get_delete_usecase),
    admin_user: dict = Depends(require_admin),
):
    result = usecase.execute(key=key)
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["message"])
    return result
