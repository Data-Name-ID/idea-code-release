import asyncio
import io
import json
from pathlib import Path
from uuid import uuid4

from litestar.datastructures import UploadFile
from litestar.exceptions import ClientException
from minio import Minio

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

        object_name = f"avatars/user-{user_id}/{uuid4().hex}{file_ext}"

        await asyncio.to_thread(
            self._client.put_object,
            self._config.bucket,
            object_name,
            io.BytesIO(data),
            len(data),
            content_type=content_type,
        )

        return (
            f"{self._config.public_base_url.rstrip('/')}/"
            f"{self._config.bucket}/{object_name}"
        )

    async def _ensure_bucket(self) -> None:
        if self._bucket_ready:
            return

        bucket = self._config.bucket
        exists = await asyncio.to_thread(self._client.bucket_exists, bucket)
        if not exists:
            await asyncio.to_thread(self._client.make_bucket, bucket)

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
        await asyncio.to_thread(
            self._client.set_bucket_policy,
            bucket,
            json.dumps(policy),
        )

        self._bucket_ready = True
