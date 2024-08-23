class DuplicateError(BaseException):
    def __init__(self, entity, traceback: str | None = None):
        self.entity = entity
        self.traceback = traceback

    def __str__(self):
        return f"{self.entity} already exists, {self.traceback}"


class DBError(BaseException):
    def __init__(self, traceback: str = ""):
        self.traceback = traceback

    def __str__(self):
        return f"Traceback: {self.traceback}"


class NotFoundError(BaseException):

    def __init__(self, entity="Entity"):
        self.entity = entity

    def __str__(self):
        return f"{self.entity} wasn't found"


class DeletionError(BaseException):
    def __init__(self, entity, info):
        def __init__(self, entity):
            self.entity = entity

        def __str__(self):
            return f"{self.entity} wasn't deleted: {info}"
