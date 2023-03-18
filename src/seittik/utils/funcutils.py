__all__ = ()


def attach(**kwargs):
    """
    Decorate a function with `func.key = value` for each key-value pair in
    `kwargs`.
    """
    def _decorator(func):
        for k, v in kwargs.items():
            setattr(func, k, v)
        return func
    return _decorator
