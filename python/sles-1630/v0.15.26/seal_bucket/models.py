import typing

from pydantic import BaseModel, HttpUrl, NonNegativeInt


class FileMetadata(BaseModel):
    etag: str
    version_id: str
    content_type: typing.Optional[str]
    metadata: typing.Dict[str, str]


class FileEntry(BaseModel):
    key: str
    etag: str
    size: NonNegativeInt


class BucketCloudfrontInfo(BaseModel):
    domain_name: HttpUrl
    signing_key_id: str
    signing_key_secret_id: str


class BucketInfo(BaseModel):
    name: str
    cloudfront: typing.Optional[BucketCloudfrontInfo] = None
