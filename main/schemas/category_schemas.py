from .base_schemas import CategoryBaseS, Id


class CreateCategoryS(CategoryBaseS):
    pass


class ReturnCategoryS(CategoryBaseS, Id):
    pass


class UpdateCategoryS(CategoryBaseS):
    pass

