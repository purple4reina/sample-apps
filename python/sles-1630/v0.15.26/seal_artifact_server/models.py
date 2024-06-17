import datetime
import enum
import typing
import uuid

import annotated_types
import seal_sealing
import seal_versions
from pydantic import (
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    model_validator,
)
from typing_extensions import Annotated

Base64 = Annotated[
    str,
    Field(
        pattern="^(?:[A-Za-z0-9+\/]{4})*(?:[A-Za-z0-9+\/]{4}|[A-Za-z0-9+\/]{3}=|[A-Za-z0-9+\/]{2}={2})$"
    ),
]

HexMd5 = Annotated[str, Field(pattern="^[a-fA-F0-9]{32}$")]

HexSha1 = Annotated[str, Field(pattern="^[a-fA-F0-9]{40}$")]

HexSha256 = Annotated[str, Field(pattern="^[a-fA-F0-9]{64}$")]

HexSha512 = Annotated[str, Field(pattern="^[a-fA-F0-9]{128}$")]


class Integrity(BaseModel):
    file_hash_md5: HexMd5
    file_hash_sha1: HexSha1
    file_hash_sha256: HexSha256
    file_hash_sha512: HexSha512


class PackageManager(enum.Enum):
    pypi = "PyPI"
    npm = "NPM"
    maven = "Maven"
    rpm = "RPM"
    go = "GO"


class ReleaseType(enum.Enum):
    source = "source"
    wheel = "wheel"
    jar = "jar"
    rpm = "rpm"
    zip = "zip"


class Architecture(enum.Enum):
    any = "any"
    x86 = "x86"
    x86_64 = "x86_64"
    arm = "arm"
    arm64 = "arm64"


class Library(BaseModel):
    id: uuid.UUID
    pretty_name: str  # the name as it appears in the UI, for example "Django" or "ReDoc"
    escaped_name: str  # the name as it appears in the URL, for example "django" or "redoc"
    sealed_name: str  # the name as it appears in the package it self, for example "seal-libtiff".
    package_manager: PackageManager
    source_link: typing.Optional[HttpUrl] = None


class LibraryCreate(BaseModel):
    pretty_name: str
    escaped_name: str
    sealed_name: str  # If not specified, it'll be filled according to sealed_name_fill
    package_manager: PackageManager
    source_link: typing.Optional[HttpUrl] = None

    @model_validator(mode="before")
    def sealed_name_fill(
        cls, values: typing.Dict[str, typing.Any]
    ) -> typing.Dict[str, typing.Any]:
        """
        If not specified, fill sealed_name with escaped_name
        Add "seal-" before if it's a RPM library
        """
        if "sealed_name" not in values:
            escaped_name = values["escaped_name"]
            # just in case package_manager received as a
            # PackageManager and not a str, compare to the enum class
            if PackageManager(values["package_manager"]) == PackageManager.rpm:
                sealed_name = f"seal-{escaped_name}"
            else:
                sealed_name = escaped_name
            values["sealed_name"] = sealed_name
        return values


class LibraryVersion(BaseModel):
    id: uuid.UUID
    library: Library
    version: str
    is_sealed: bool
    origin_version: typing.Optional[str] = None
    origin_version_id: typing.Optional[uuid.UUID] = None
    previous_version: typing.Optional[str] = None
    previous_version_id: typing.Optional[uuid.UUID] = None
    recommended_version: typing.Optional[str] = None
    recommended_version_id: typing.Optional[uuid.UUID] = None
    patch_pre_signed_url: typing.Optional[HttpUrl] = None
    source_ref_url: typing.Optional[HttpUrl] = None
    patch_stage: typing.Optional[seal_sealing.models.Stage] = None
    publish_date: typing.Optional[AwareDatetime] = None


class LibraryVersionUpdate(BaseModel):
    """
    This is the model used to update a library version.
    Currently we don't support updating all fields, as it might create edge cases with chaining versions.
    """

    is_sealed: bool
    version: seal_versions.Version
    version_level_patch_content_base64: typing.Optional[Base64] = None
    source_ref_url: typing.Optional[HttpUrl] = None
    patch_stage: typing.Optional[seal_sealing.models.Stage] = None
    publish_date: typing.Optional[AwareDatetime] = None


class LibraryVersionCreate(LibraryVersionUpdate):
    library_id: uuid.UUID
    previous_version: typing.Optional[
        seal_versions.Version
    ] = None  # None if it's the public version


class Artifact(BaseModel):
    id: uuid.UUID
    library_version: LibraryVersion
    file_name: str
    file_size: int
    integrity: Integrity
    release_date: AwareDatetime
    bucket_key: str
    signature: typing.Optional[str] = None
    pre_signed_url: HttpUrl
    pre_signed_head_url: HttpUrl
    interpreter: typing.Optional[str] = None
    interpreter_version: typing.Optional[str] = None
    operating_system: typing.Optional[str] = None
    architecture: typing.Optional[Architecture] = None
    release_type: typing.Optional[ReleaseType] = None
    additional_info: typing.Optional[typing.Dict[str, typing.Any]] = None


class ArtifactCreate(BaseModel):
    library_version_id: uuid.UUID
    file_name: str
    upload_bucket_key: str  # to download the file from, due to lambda's 6MB cap
    content_type: str
    signature: typing.Optional[str] = None
    release_date: AwareDatetime
    interpreter: typing.Optional[str] = None
    interpreter_version: typing.Optional[str] = None
    operating_system: typing.Optional[str] = None
    architecture: typing.Optional[Architecture] = None
    release_type: typing.Optional[ReleaseType] = None
    additional_info: typing.Optional[typing.Dict[str, typing.Any]] = None


VulnerabilityScore = Annotated[float, annotated_types.Ge(0), annotated_types.Le(10)]


class Vulnerability(BaseModel):
    id: uuid.UUID
    library: Library
    version_ranges: str
    publication_date: datetime.date
    modified_on: AwareDatetime
    cve: typing.Optional[str] = None
    nvd_score: typing.Optional[VulnerabilityScore] = None
    snyk_id: typing.Optional[str] = None
    snyk_cvss_score: typing.Optional[VulnerabilityScore] = None
    github_advisory_id: typing.Optional[str] = None
    github_advisory_score: typing.Optional[VulnerabilityScore] = None
    malicious_id: typing.Optional[str] = None
    is_withdrawn: bool


class VersionRange(BaseModel):
    start: seal_versions.Version
    end: typing.Optional[seal_versions.Version] = None

    @model_validator(mode="after")
    def validate_end_is_after_start(self) -> "VersionRange":
        if self.end is not None:
            assert (
                self.start < self.end
            ), "End version ({}) must be after start ({}) version".format(
                self.end, self.start
            )
        return self

    def __str__(self) -> str:
        if self.end is None:
            # no end version
            return f"[{self.start},)"
        else:
            # range with end version
            return f"[{self.start}, {self.end})"

    def __lt__(self, other: "VersionRange") -> bool:
        if self.start != other.start:
            return self.start < other.start
        if self.end is None:
            return False
        if other.end is None:
            return True
        return self.end < other.end


# TODO: validate version ranges are not overlapping
VersionRangeList = Annotated[typing.List[VersionRange], annotated_types.MinLen(1)]


class VulnerabilityUpdate(BaseModel):
    publication_date: datetime.date
    cve: typing.Optional[str] = None
    nvd_score: typing.Optional[VulnerabilityScore] = None
    snyk_id: typing.Optional[str] = None
    snyk_cvss_score: typing.Optional[VulnerabilityScore] = None
    github_advisory_id: typing.Optional[str] = None
    github_advisory_score: typing.Optional[VulnerabilityScore] = None
    malicious_id: typing.Optional[str] = None
    is_withdrawn: bool

    @model_validator(mode="before")
    def check(
        cls,
        values: typing.Dict[str, typing.Any],
    ) -> typing.Dict[str, typing.Any]:
        cve, snyk_id, github_advisory_id, malicious_id = (
            values.get("cve"),
            values.get("snyk_id"),
            values.get("github_advisory_id"),
            values.get("malicious_id"),
        )
        if (
            cve is None
            and snyk_id is None
            and github_advisory_id is None
            and malicious_id is None
        ):
            raise ValueError(
                "missing cve, snyk_id, github_advisory_id and malicious_id"
            )
        return values


class VulnerabilityCreate(VulnerabilityUpdate):
    library_id: uuid.UUID
    version_ranges: VersionRangeList


class VulnerabilityImpact(BaseModel):
    id: uuid.UUID
    library_version_id: uuid.UUID
    vulnerability_id: uuid.UUID
    is_fix: bool
    vulnerability_patch_bucket_key: typing.Optional[str] = None
    vulnerability_patch_pre_signed_url: typing.Optional[HttpUrl] = None


class VulnerabilityImpactCreate(BaseModel):
    library_version_id: uuid.UUID
    vulnerability_id: uuid.UUID
    is_fix: bool
    vulnerability_patch_content_base64: typing.Optional[Base64] = None
    add_to_ancestors: bool = True


class PublicLibraryIdentifier(BaseModel):
    model_config = ConfigDict(frozen=True)

    library_name: str
    library_version: str
    library_package_manager: str


class PublicLibraryIdentifierList(BaseModel):
    entries: typing.List[PublicLibraryIdentifier]
