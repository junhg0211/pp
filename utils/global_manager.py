_globals = dict()


def set_global(key: str, value):
    _globals[key] = value
    return value


def get_global(key: str):
    return _globals[key]
