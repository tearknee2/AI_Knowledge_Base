
class AppException(Exception):
    def __init__(
        self,
        message: str,
        code: str,
        status_code: int
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code

class ResourceNotFoundError(AppException):
    def __init__(self):
        super().__init__(
            message="资源不存在或无权访问",
            code="RESOURCE_NOT_FOUND",
            status_code=404
        )

class ConflictError(AppException):
    def __init__(self):
        super().__init__(
            message="资源已存在",
            code="RESOURCE_ALREADY_EXISTS",
            status_code=409
        )

class AuthenticationError(AppException):
    def __init__(self):
        super().__init__(
            message="身份认证失败",
            code="AUTHENTICATION_FAILED",
            status_code=401
        )

class LLMUnavailableError(AppException):
    def __init__(self):
        super().__init__(
            message="大模型服务暂时不可用",
            code="LLM_SERVICE_UNAVAILABLE",
            status_code=502
        )

class StorageError(AppException):
    def __init__(self):
        super().__init__(
            message="存储服务暂时不可用",
            code="STORAGE_ERROR",
            status_code=500
        )