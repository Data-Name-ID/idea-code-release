import asyncio
import io
import json
from pathlib import Path
from urllib.parse import urlparse
from uuid import uuid4

from litestar.datastructures import UploadFile
from litestar.exceptions import ClientException
from minio import Minio
from minio.error import S3Error

from app.core.config import ObjectStorageConfig


class ObjectStorageService:
    def __init__(self, config: ObjectStorageConfig) -> None:
        self._config = config
        self._client = Minio(
            endpoint=config.endpoint,
            access_key=config.access_key,
            secret_key=config.secret_key,
            secure=config.secure,
        )
        self._bucket_ready = False

    async def upload_avatar(self, *, user_id: int, upload_file: UploadFile) -> str:
        content_type = upload_file.content_type or ""
        if not content_type.startswith("image/"):
            msg = "Avatar file must be an image"
            raise ClientException(status_code=400, detail=msg)

        data = await upload_file.read()
        if not data:
            msg = "Avatar file is empty"
            raise ClientException(status_code=400, detail=msg)

        max_size_bytes = self._config.max_upload_size_mb * 1024 * 1024
        if len(data) > max_size_bytes:
            msg = f"Avatar is too large (max {self._config.max_upload_size_mb} MB)"
            raise ClientException(status_code=400, detail=msg)

        await self._ensure_bucket()

        file_ext = Path(upload_file.filename or "").suffix.lower()
        if not file_ext:
            file_ext = ".jpg" if content_type == "image/jpeg" else ".png"

        object_name = f"user-{user_id}/{uuid4().hex}{file_ext}"

        await asyncio.to_thread(
            self._client.put_object,
            self._config.bucket,
            object_name,
            io.BytesIO(data),
            len(data),
            content_type=content_type,
        )

        return self._build_public_url(object_name=object_name)

    async def _ensure_bucket(self) -> None:
        if self._bucket_ready:
            return

        bucket = self._config.bucket
        try:
            exists = await asyncio.to_thread(self._client.bucket_exists, bucket)
        except S3Error as exc:
            # In external S3 setups list/read bucket metadata can be forbidden,
            # while PutObject is still allowed for a pre-created bucket.
            if exc.code in {"AccessDenied", "MethodNotAllowed", "NotImplemented"}:
                self._bucket_ready = True
                return
            raise

        if not exists:
            try:
                await asyncio.to_thread(self._client.make_bucket, bucket)
            except S3Error as exc:
                if exc.code not in {
                    "BucketAlreadyOwnedByYou",
                    "BucketAlreadyExists",
                    "AccessDenied",
                }:
                    raise

        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": ["*"]},
                    "Action": ["s3:GetObject"],
                    "Resource": [f"arn:aws:s3:::{bucket}/*"],
                },
            ],
        }
        try:
            await asyncio.to_thread(
                self._client.set_bucket_policy,
                bucket,
                json.dumps(policy),
            )
        except S3Error as exc:
            if exc.code not in {
                "AccessDenied",
                "MethodNotAllowed",
                "NotImplemented",
                "MalformedPolicy",
            }:
                raise

        self._bucket_ready = True

    def _build_public_url(self, *, object_name: str) -> str:
        base_url = self._config.public_base_url.rstrip("/")
        bucket = self._config.bucket
        include_bucket = self._config.public_include_bucket

        if include_bucket is True:
            return f"{base_url}/{bucket}/{object_name}"
        if include_bucket is False:
            return f"{base_url}/{object_name}"

        parsed = urlparse(base_url)
        host = parsed.netloc.lower()
        path = parsed.path.rstrip("/")
        bucket_marker = f"/{bucket}".lower()

        bucket_in_host = host.startswith(f"{bucket.lower()}.")
        bucket_in_path = path.lower() == bucket_marker or path.lower().endswith(
            bucket_marker,
        )
        if bucket_in_host or bucket_in_path:
            return f"{base_url}/{object_name}"
        return f"{base_url}/{bucket}/{object_name}"
