import base64
import datetime
import hashlib
import io
import typing

from pydantic import AwareDatetime, HttpUrl
from seal_logging import logger

from . import exceptions, models
from .client import Client
from .settings import Settings


class Service:
    ttl_tag = "expires_on_epoch"

    def __init__(
        self,
        settings: Settings,
        client: Client,
    ) -> None:
        self._client = client
        self._settings = settings

    def generate_presigned_url(
        self,
        bucket_name: str,
        bucket_key: str,
        ttl: datetime.timedelta,
        http_method: str = "GET",
    ) -> HttpUrl:
        # generate a temporary URL to download
        logger.debug(
            "lib-bucket generating signed url for s3://%s/%s for %s",
            bucket_name,
            bucket_key,
            ttl,
        )
        response = self._client.s3_client.generate_presigned_url(
            ClientMethod="get_object",
            Params={
                "Bucket": bucket_name,
                "Key": bucket_key,
            },
            ExpiresIn=int(ttl.total_seconds()),
            HttpMethod=http_method,
        )
        # The response contains the presigned URL
        logger.debug(
            "lib-bucket generated signed url for s3://%s/%s for %s",
            bucket_name,
            bucket_key,
            ttl,
        )
        return HttpUrl(response)

    def get_file_with_metadata(
        self,
        bucket_name: str,
        bucket_key: str,
        version_id: typing.Optional[str] = None,
    ) -> typing.Tuple[bytes, models.FileMetadata]:
        logger.debug(
            "lib-bucket reading file from s3://%s/%s -> version %s",
            bucket_name,
            bucket_key,
            version_id,
        )

        optional_arguments: typing.Dict[str, typing.Any] = {}

        if version_id is not None:
            optional_arguments["VersionId"] = version_id

        try:
            response = self._client.s3_client.get_object(
                Bucket=bucket_name,
                Key=bucket_key,
                **optional_arguments,
            )
        except self._client.s3_client.exceptions.NoSuchKey:
            raise exceptions.NoSuchFileException(
                f"File not found in bucket {bucket_name} with key {bucket_key}"
            )

        metadata = response["Metadata"]
        if self.ttl_tag in metadata:
            expiration_time = self._get_ttl_from_tag(metadata[self.ttl_tag])
            if expiration_time < datetime.datetime.now(tz=datetime.timezone.utc):
                raise exceptions.FileExpiredException(
                    f"File expired in bucket at {expiration_time}"
                )

        file_metadata = models.FileMetadata(
            etag=response["ETag"],
            version_id=response["VersionId"],
            content_type=response.get("ContentType", None),
            metadata=response.get("Metadata", {}),
        )

        return response["Body"].read(), file_metadata

    def get_file(
        self,
        bucket_name: str,
        bucket_key: str,
        version_id: typing.Optional[str] = None,
    ) -> bytes:
        content, _ = self.get_file_with_metadata(
            bucket_name=bucket_name,
            bucket_key=bucket_key,
            version_id=version_id,
        )
        return content

    def put_file(
        self,
        bucket_name: str,
        bucket_key: str,
        content: typing.Union[str, bytes, typing.IO[typing.Any]],
        content_type: typing.Optional[str] = None,
        content_disposition: typing.Optional[str] = None,
        ttl: typing.Optional[datetime.timedelta] = None,
    ) -> str:
        logger.debug(
            "lib-bucket writing file to s3://%s/%s",
            bucket_name,
            bucket_key,
        )
        optional_arguments: typing.Dict[str, typing.Any] = {}
        metadata: typing.Dict[str, str] = {}

        if content_type is not None:
            optional_arguments["ContentType"] = content_type
        if content_disposition is not None:
            optional_arguments["ContentDisposition"] = content_disposition
        if ttl is not None:
            metadata[self.ttl_tag] = self._get_ttl_tag_content(ttl=ttl)

        # move the cursor to the beginning of the file
        if isinstance(content, io.IOBase):
            content.seek(0)

        content_sha256 = self._get_content_sha256(content)
        response = self._client.s3_client.put_object(
            Bucket=bucket_name,
            Key=bucket_key,
            Body=content,
            ChecksumSHA256=content_sha256,
            ACL="private",
            Metadata=metadata,
            **optional_arguments,
        )
        version_id = response["VersionId"]
        response_checksum = response["ChecksumSHA256"]
        if content_sha256 != response_checksum:
            logger.error(
                "lib-bucket wrote file to s3://%s/%s -> version %s but checksums do not match",
                bucket_name,
                bucket_key,
                version_id,
            )
            raise ValueError("Checksums do not match")
        logger.debug(
            "lib-bucket wrote file to s3://%s/%s -> version %s",
            bucket_name,
            bucket_key,
            version_id,
        )
        return version_id

    def copy_file(
        self,
        source_bucket_name: str,
        source_bucket_key: str,
        destination_bucket_name: str,
        destination_bucket_key: str,
        content_type: typing.Optional[str] = None,
        content_disposition: typing.Optional[str] = None,
    ) -> str:
        logger.debug(
            "lib-bucket copying s3://%s/%s -> s3://%s/%s",
            source_bucket_name,
            source_bucket_key,
            destination_bucket_name,
            destination_bucket_key,
        )

        if (
            source_bucket_name == destination_bucket_name
            and source_bucket_key == destination_bucket_key
        ):
            raise exceptions.SameSourceAndDestinationException

        optional_arguments: typing.Dict[str, typing.Any] = {}

        if content_type is not None:
            optional_arguments["ContentType"] = content_type
        if content_disposition is not None:
            optional_arguments["ContentDisposition"] = content_disposition

        response = self._client.s3_client.copy_object(
            Bucket=destination_bucket_name,
            Key=destination_bucket_key,
            ACL="private",
            MetadataDirective="REPLACE",  # replace content type and content disposition
            TaggingDirective="COPY",
            CopySource={
                "Bucket": source_bucket_name,
                "Key": source_bucket_key,
            },
            **optional_arguments,
        )
        version_id = response["VersionId"]
        logger.debug(
            "lib-bucket copied s3://%s/%s -> s3://%s/%s -> version %s",
            source_bucket_name,
            source_bucket_key,
            destination_bucket_name,
            destination_bucket_key,
            version_id,
        )
        return version_id

    def delete_file(
        self,
        bucket_name: str,
        bucket_key: str,
        version_id: typing.Optional[str] = None,
    ) -> None:
        optional_arguments: typing.Dict[str, typing.Any] = {}
        if version_id is not None:
            optional_arguments["VersionId"] = version_id

        self._client.s3_client.delete_object(
            Bucket=bucket_name,
            Key=bucket_key,
            **optional_arguments,
        )

    def list_files(
        self,
        bucket_name: str,
        prefix: typing.Optional[str] = None,
    ) -> typing.Generator[models.FileEntry, None, None]:
        has_more_pages = True
        continuation_token = None

        while has_more_pages:
            optional_arguments: typing.Dict[str, typing.Any] = {}
            if continuation_token is not None:
                optional_arguments["ContinuationToken"] = continuation_token
            if prefix is not None:
                optional_arguments["Prefix"] = prefix
            response = self._client.s3_client.list_objects_v2(
                Bucket=bucket_name,
                **optional_arguments,
            )
            has_more_pages = response["IsTruncated"]
            continuation_token = response["NextContinuationToken"]

            for content in response["Contents"]:
                yield models.FileEntry(
                    key=content["Key"],
                    etag=content["ETag"],
                    size=content["Size"],
                )

    @classmethod
    def _get_content_sha256(
        cls,
        content: typing.Union[str, bytes, typing.IO[typing.Any]],
    ) -> str:
        sha256 = hashlib.sha256()
        if isinstance(content, bytes):
            sha256.update(content)
        elif isinstance(content, str):
            sha256.update(content.encode("utf-8"))
        else:
            # read the content and move the cursor back
            cursor_location = content.tell()
            sha256.update(content.read())
            content.seek(cursor_location)
        return base64.b64encode(sha256.digest()).decode("utf-8")

    @classmethod
    def _get_ttl_tag_content(
        cls,
        ttl: datetime.timedelta,
    ) -> str:
        expiration_time = datetime.datetime.now(tz=datetime.timezone.utc) + ttl
        return str(int(expiration_time.timestamp()))

    @classmethod
    def _get_ttl_from_tag(
        cls,
        tag_content: str,
    ) -> AwareDatetime:
        return datetime.datetime.fromtimestamp(
            int(tag_content), tz=datetime.timezone.utc
        )
