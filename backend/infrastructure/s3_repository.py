from botocore.exceptions import ClientError

from backend.domain.storage_entity import S3ObjectNotFoundError, S3PermissionError, S3StorageError


class S3Repository:
    # Cấp 4: Giao tiếp với S3. YAGNI: Không chứa business rule.

    def __init__(self, client, bucket: str):
        self._client = client
        self._bucket = bucket

    @property
    def bucket(self) -> str:
        return self._bucket

    def _wrap_client_error(self, error: ClientError) -> Exception:
        code = error.response["Error"]["Code"]
        if code in ("404", "NoSuchKey"):
            return S3ObjectNotFoundError(str(error))
        if code in ("403", "AccessDenied"):
            return S3PermissionError(str(error))
        return S3StorageError(str(error))

    def put_object_bytes(
        self, key: str, data: bytes, content_type: str, metadata: dict | None = None
    ) -> None:
        kwargs = {
            "Bucket": self._bucket,
            "Key": key,
            "Body": data,
            "ContentType": content_type,
        }
        if metadata:
            kwargs["Metadata"] = {k: str(v) for k, v in metadata.items()}
        try:
            self._client.put_object(**kwargs)
        except ClientError as e:
            raise self._wrap_client_error(e) from e

    def get_object_bytes(self, key: str) -> bytes:
        try:
            response = self._client.get_object(Bucket=self._bucket, Key=key)
            return response["Body"].read()
        except ClientError as e:
            raise self._wrap_client_error(e) from e

    def delete_object(self, key: str) -> None:
        try:
            self._client.delete_object(Bucket=self._bucket, Key=key)
        except ClientError as e:
            raise self._wrap_client_error(e) from e

    def list_objects(self, prefix: str) -> list[dict]:
        try:
            response = self._client.list_objects_v2(Bucket=self._bucket, Prefix=prefix)
            return response.get("Contents", [])
        except ClientError as e:
            raise self._wrap_client_error(e) from e

    def generate_presigned_url(self, key: str, expires_in: int = 3600) -> str:
        try:
            return self._client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self._bucket, "Key": key},
                ExpiresIn=expires_in,
            )
        except ClientError as e:
            raise self._wrap_client_error(e) from e

    def object_exists(self, key: str) -> bool:
        try:
            self._client.head_object(Bucket=self._bucket, Key=key)
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] in ("404", "NoSuchKey"):
                return False
            raise self._wrap_client_error(e) from e
