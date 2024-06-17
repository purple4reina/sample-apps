import typing


class SealLambdaInvokeException(Exception):
    pass


class SealLambdaInvokeHttpException(SealLambdaInvokeException):
    def __init__(
        self,
        status_code: typing.Optional[int],
        content: typing.Optional[str] = None,
        msg: typing.Optional[str] = None,
    ) -> None:
        super().__init__(msg)
        self.status_code = status_code
        self.content = content
