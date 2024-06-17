class SealArtifactServerException(Exception):
    pass


class ArtifactNotFound(SealArtifactServerException):
    pass


class LibraryVersionNotFound(SealArtifactServerException):
    pass


class ArtifactManagementError(SealArtifactServerException):
    pass


class ArtifactManagementMoreThanOnArtifactForFile(ArtifactManagementError):
    pass


class ArtifactManagementMoreThanOneLibraryForVersion(ArtifactManagementError):
    pass


class InvalidArguments(Exception):
    pass


class LibraryCreateFailed(SealArtifactServerException):
    pass


class LibraryVersionCreateFailed(SealArtifactServerException):
    pass


class LibraryVersionUpdateFailed(SealArtifactServerException):
    pass


class LibraryVersionAlreadyExists(LibraryVersionCreateFailed):
    pass


class VulnerabilityCreateFailed(SealArtifactServerException):
    pass


class VulnerabilityAlreadyExists(VulnerabilityCreateFailed):
    pass


class VulnerabilityImpactCreateFailed(SealArtifactServerException):
    pass


class ArtifactCreateFailed(SealArtifactServerException):
    pass


class VulnerabilityUpdateFailed(SealArtifactServerException):
    pass


class BadVersionFormat(SealArtifactServerException):
    pass
