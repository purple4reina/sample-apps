class SealBucketException(Exception):
    pass


class NoSuchFileException(SealBucketException):
    pass


class FileExpiredException(SealBucketException):
    pass


class SameSourceAndDestinationException(SealBucketException):
    pass
