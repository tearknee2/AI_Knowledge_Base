from app.core.exceptions import (
    ResourceNotFoundError,
    ConflictError,
    AuthenticationError,
    LLMUnavailableError,
    StorageError,
)

errors = [
    ResourceNotFoundError(),
    ConflictError(),
    AuthenticationError(),
    LLMUnavailableError(),
    StorageError(),
]

for error in errors:
    print(
        type(error).__name__,
        error.message,
        error.code,
        error.status_code,
        str(error)
    )