REQUEST_INVALID_ERR = "request_invalid_error"
INTERNAL_ERR = "internal_error"


class RError(Exception):
    def __init__(
            self,
            message,
            cause: Exception = None
    ):
        super(RError, self).__init__(message, cause)
        self.message = message
        self.__cause__ = cause

    def get_message(self) -> str:
        return self.message

    def get_error(self) -> str:
        pass


class RequestInvalidError(RError):
    def __init__(
            self,
            message,
            cause: Exception = None):
        super(RequestInvalidError, self).__init__(
            message, cause
        )

    def get_error(self) -> str:
        return REQUEST_INVALID_ERR


class InternalError(RError):
    def __init__(
            self,
            message,
            cause: Exception = None):
        super(InternalError, self).__init__(
            message, cause
        )

    def get_error(self) -> str:
        return INTERNAL_ERR
