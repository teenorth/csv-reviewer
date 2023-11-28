class ApiExceptionBase(Exception):
    def __init__(
        self, message="An API error occurred (no message provided)", status_code=500
    ):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class RecordNotUnique(ApiExceptionBase):
    pass


class RecordNotFound(ApiExceptionBase):
    pass


class UnauthorizedAccess(ApiExceptionBase):
    pass


class ReviewCommitted(ApiExceptionBase):
    pass


class NoFileAttached(ApiExceptionBase):
    pass


class NoFileSelected(ApiExceptionBase):
    pass


class DocumentNotFound(ApiExceptionBase):
    def __init__(self, message="Document ID does not exist", status_code=404):
        super().__init__(message, status_code)
