from core.exceptions import FilterAttributeError


def sth():
    arr = []
    try:
        try:
            arr.rem()
        except AttributeError as e:
            raise  FilterAttributeError
    except FilterAttributeError as e:
        print(str(e))

sth()
