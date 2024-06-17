import re
import typing

import annotated_types
from pydantic import BaseModel, FieldValidationInfo, field_validator, model_validator
from typing_extensions import Annotated

from . import exceptions

VERSION_REGEX = re.compile(
    r"^((?P<epoch>\d+):)?"
    r"(?P<major>0|[1-9]\d*)"
    r"(\.(?P<minor>0|[1-9]\d*))?"
    r"(\.(?P<patch>0|[1-9]\d*))?"
    r"(\.(?P<tiny>0|[1-9]\d*))?"
    r"(?P<suffix>[a-zA-Z\-_\+\.][\d\.a-zA-Z\-_\+]+)?$"
)


NonNegativeNumber = Annotated[int, annotated_types.Ge(0)]


class Version(BaseModel):
    """
    A version of a software package.

    Notice that this implementation is not semver compliant as semver deffer between Python and Node.
    The differences are:
    * We allow `build` component not to start with a `+` sign.
    * We define order between different build versions.
    * We allow minor and patch versions to be None.
    """

    epoch: typing.Optional[NonNegativeNumber] = None
    major: NonNegativeNumber
    minor: typing.Optional[NonNegativeNumber] = None
    patch: typing.Optional[NonNegativeNumber] = None
    tiny: typing.Optional[NonNegativeNumber] = None
    pre_release: typing.Optional[str] = None
    build: typing.Optional[str] = None

    @model_validator(mode="after")
    def validate_tiny_can_exist_only_if_patch(self) -> "Version":
        if self.patch is None and self.tiny is not None:
            raise exceptions.MissingVersionValue("has tiny but missing patch")
        return self

    @model_validator(mode="after")
    def string_representation_consistency(self) -> "Version":
        (
            epoch,
            major,
            minor,
            patch,
            tiny,
            pre_release,
            build,
        ) = self._values_from_string(self._version_to_string(**self.model_dump()))
        if (
            major != self.major
            or self._lt_for_nullable_int(epoch, self.epoch) is not None
            or self._lt_for_nullable_int(minor, self.minor) is not None
            or self._lt_for_nullable_int(patch, self.patch) is not None
            or self._lt_for_nullable_int(tiny, self.tiny) is not None
            or pre_release != self.pre_release
            or build != self.build
        ):
            raise exceptions.InconsistentVersionException()
        return self

    @field_validator("pre_release", "build")
    def not_empty(
        cls, value: typing.Optional[str], field: FieldValidationInfo
    ) -> typing.Optional[str]:
        if value == "":
            raise exceptions.MissingVersionValue(f"Cannot be empty: {field.field_name}")
        return value

    def __str__(self) -> str:
        return self._version_to_string(
            epoch=self.epoch,
            major=self.major,
            minor=self.minor,
            patch=self.patch,
            tiny=self.tiny,
            pre_release=self.pre_release,
            build=self.build,
        )

    @staticmethod
    def _version_to_string(
        major: NonNegativeNumber,
        minor: typing.Optional[NonNegativeNumber] = None,
        patch: typing.Optional[NonNegativeNumber] = None,
        tiny: typing.Optional[NonNegativeNumber] = None,
        pre_release: typing.Optional[str] = None,
        build: typing.Optional[str] = None,
        epoch: typing.Optional[NonNegativeNumber] = None,
    ) -> str:
        version_str = str(major)
        if epoch is not None:
            version_str = f"{epoch}:{version_str}"
        if minor is not None:
            version_str += f".{minor}"
        if patch is not None:
            version_str += f".{patch}"
        if tiny is not None:
            version_str += f".{tiny}"
        if pre_release is not None:
            version_str += pre_release
        if build is not None:
            version_str += build
        return version_str

    @staticmethod
    def _lt_for_nullable_int(
        this_element: typing.Optional[int], other_element: typing.Optional[int]
    ) -> typing.Optional[bool]:
        if (
            this_element != other_element
            # None and 0 are equal
            and not (this_element is None and other_element == 0)
            and not (this_element == 0 and other_element is None)
        ):
            if this_element is None:
                return True
            if other_element is None:
                return False
            return this_element < other_element
        return None

    def __hash__(self) -> int:
        """
        to allow using set and prevent duplicate versions
        """
        hashable = (
            self.epoch if self.epoch is not None else 0,
            self.major,
            self.minor if self.minor is not None else 0,
            self.patch if self.patch is not None else 0,
            self.tiny if self.tiny is not None else 0,
            self.pre_release if self.pre_release is not None else "",
            self.build if self.build is not None else "",
        )
        return hashable.__hash__()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Version):
            raise NotImplementedError()
        return self.__hash__() == other.__hash__()

    def __lt__(self, other: "Version") -> bool:
        # epoch
        epoch_lt = self._lt_for_nullable_int(self.epoch, other.epoch)
        if epoch_lt is not None:
            return epoch_lt
        # major
        if self.major != other.major:
            return self.major < other.major
        # minor
        minor_lt = self._lt_for_nullable_int(self.minor, other.minor)
        if minor_lt is not None:
            return minor_lt
        # patch
        patch_lt = self._lt_for_nullable_int(self.patch, other.patch)
        if patch_lt is not None:
            return patch_lt
        # tiny
        tiny_lt = self._lt_for_nullable_int(self.tiny, other.tiny)
        if tiny_lt is not None:
            return tiny_lt
        # pre-release
        if self.pre_release != other.pre_release:
            if self.pre_release is None:
                return False
            if other.pre_release is None:
                return True
            return self.pre_release < other.pre_release
        # build
        if self.build != other.build:
            if self.build is None:
                return True
            if other.build is None:
                return False
            return self.build < other.build

        # equal
        return False

    @classmethod
    def _is_pre_release_from_suffix(cls, suffix: typing.Optional[str]) -> bool:
        if suffix is None:
            return False
        return any(suffix.startswith(prefix) for prefix in ("-", "rc", ".rc"))

    @classmethod
    def from_string(cls, version_str: str) -> "Version":
        (
            epoch,
            major,
            minor,
            patch,
            tiny,
            pre_release,
            build,
        ) = cls._values_from_string(version_str=version_str)
        return cls(
            epoch=epoch,
            major=major,
            minor=minor,
            patch=patch,
            tiny=tiny,
            pre_release=pre_release,
            build=build,
        )

    @classmethod
    def _values_from_string(
        cls, version_str: str
    ) -> typing.Tuple[
        typing.Optional[NonNegativeNumber],
        NonNegativeNumber,
        typing.Optional[NonNegativeNumber],
        typing.Optional[NonNegativeNumber],
        typing.Optional[NonNegativeNumber],
        typing.Optional[str],
        typing.Optional[str],
    ]:
        match = VERSION_REGEX.match(version_str)
        if match is None:
            raise exceptions.BadVersionFormatException(
                f"Invalid version string: {version_str}"
            )
        epoch = match.group("epoch")
        major = match.group("major")
        minor = match.group("minor")
        patch = match.group("patch")
        tiny = match.group("tiny")
        suffix = match.group("suffix")
        if cls._is_pre_release_from_suffix(suffix):
            pre_release = suffix
            build = None
            plus_index = suffix.find("+")
            if plus_index != -1:
                pre_release = suffix[:plus_index]
                build = suffix[plus_index:]
        else:
            pre_release = None
            build = suffix
        return (
            int(epoch) if epoch is not None else None,
            int(major),
            int(minor) if minor is not None else None,
            int(patch) if patch is not None else None,
            int(tiny) if tiny is not None else None,
            pre_release,
            build,
        )
