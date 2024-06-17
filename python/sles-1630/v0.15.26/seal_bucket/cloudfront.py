import datetime
import urllib.parse

from botocore.signers import CloudFrontSigner
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from pydantic import AwareDatetime, HttpUrl
from seal_logging import logger


class Signer:
    def __init__(
        self,
        domain_name: HttpUrl,
        signing_key_id: str,
        signing_private_key: str,
    ) -> None:
        self._domain_name = domain_name
        self._signing_key_id = signing_key_id

        private_key = serialization.load_pem_private_key(
            data=signing_private_key.encode("utf-8"),
            password=None,
            backend=default_backend(),
        )
        if not isinstance(private_key, rsa.RSAPrivateKey):
            raise ValueError("signing_private_key must be an RSA private key")
        self._private_key = private_key
        self._cloudfront_signer = CloudFrontSigner(
            key_id=self._signing_key_id,
            rsa_signer=self._rsa_signer,
        )

    def generate_presigned_url(
        self,
        bucket_key: str,
        ttl: datetime.timedelta,
    ) -> HttpUrl:
        # based on https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudfront.html#generate-a-signed-url-for-amazon-cloudfront
        # generate a temporary URL to download
        logger.debug(
            "lib-bucket generating signed url for cloudfront %s/%s for %s",
            self._domain_name,
            bucket_key,
            ttl,
        )
        expire_date = self._calculate_expiration_date(ttl=ttl)
        url = urllib.parse.urljoin(
            str(self._domain_name),
            bucket_key,
        )

        signed_url = self._cloudfront_signer.generate_presigned_url(
            url=url,
            date_less_than=expire_date,
        )

        # The response contains the presigned URL
        logger.debug(
            "lib-bucket generated signed url for cloudfront %s/%s for %s",
            self._domain_name,
            bucket_key,
            ttl,
        )
        return HttpUrl(signed_url)

    def _rsa_signer(self, message: bytes) -> bytes:
        return self._private_key.sign(
            data=message, padding=padding.PKCS1v15(), algorithm=hashes.SHA1()
        )

    @classmethod
    def _calculate_expiration_date(cls, ttl: datetime.timedelta) -> AwareDatetime:
        return datetime.datetime.now(tz=datetime.timezone.utc) + ttl
