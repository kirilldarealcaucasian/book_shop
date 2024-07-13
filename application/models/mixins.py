from sqlalchemy.orm import validates


__all__ = (
    "FirstLastNameValidationMixin",
)


class FirstLastNameValidationMixin:

    @validates("first_name")
    def validate_first_name(self, key, name):
        if len(name) < 2:
            raise ValueError(
                "First name should be at least 2 characters"
            )
        return name

    @validates("last_name")
    def validate_last_name(self, key, last_name):
        if len(last_name) < 2:
            raise ValueError(
                "Last name should be at least 2 characters"
            )
        return last_name