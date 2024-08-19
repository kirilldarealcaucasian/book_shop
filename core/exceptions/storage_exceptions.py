class DuplicateError(BaseException):
    def __init__(self, entity, traceback: str | None):
        self.entity = entity
        self.traceback = traceback

    def __str__(self):
        return f"{self.entity} already exists, {self.traceback}"


class DBError(BaseException):
    def __init__(self, message: str, traceback: str = ""):
        self.message = message
        self.traceback = traceback

    def __str__(self):
        return f"{self.message}: {self.traceback}"


class NotFoundError(BaseException):

    def __str__(self):
        return "Entity wasn't found"


class DeletionError(BaseException):
    def __init__(self, entity, info):
        def __init__(self, entity):
            self.entity = entity

        def __str__(self):
            return f"{self.entity} wasn't deleted: {info}"
