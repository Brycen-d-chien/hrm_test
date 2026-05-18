import mimetypes


def parse_s3_uri(uri: str) -> tuple[str, str]:
    """Parse 's3://bucket/key/path' -> ('bucket', 'key/path')."""
    if not uri.startswith("s3://"):
        raise ValueError(f"URI không hợp lệ, phải bắt đầu bằng 's3://': {uri}")
    without_scheme = uri[5:]
    bucket, _, key = without_scheme.partition("/")
    return bucket, key


def detect_content_type(filename: str) -> str:
    """Detect MIME type từ extension. Fallback về 'application/octet-stream'."""
    content_type, _ = mimetypes.guess_type(filename)
    return content_type or "application/octet-stream"


def extract_object_list(response: dict) -> list[dict]:
    """Trích xuất danh sách object từ response của list_objects_v2."""
    return response.get("Contents", [])
