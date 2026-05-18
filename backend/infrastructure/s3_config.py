import os
import boto3


def get_s3_client():
    return boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION", "ap-southeast-1"),
        # None = dùng AWS mặc định; set URL cho MinIO/LocalStack
        endpoint_url=os.getenv("S3_ENDPOINT_URL") or None,
    )


def get_s3_bucket() -> str:
    return os.getenv("S3_BUCKET", "hrm-bucket")
