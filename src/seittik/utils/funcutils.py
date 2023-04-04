from functools import wraps
import inspect

from .sentinels import _MISSING


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


def multilambda(param, optional=_MISSING):
    """
    Decorate a function so that if parameter `param` is not provided, a
    partial function suitable as a decorator is returned instead.

    Intended to be used with parameter defaults that are identity sentinels,
    tested with `is` rather than `==`.

    If `optional` is provided, the return of a partial function will only
    take place if `param`'s argument value is the value provided for
    `optional`.
    """
    def _decorator(func):
        sig = inspect.signature(func)
        for k, p in sig.parameters.items():
            if k != param:
                continue
            default = p.default if optional is _MISSING else optional
            if p.kind not in {inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.KEYWORD_ONLY} or default is inspect._empty:
                raise TypeError(f"param {param!r} must be a keyword parameter with a default")
            break
        else:
            raise ValueError(f"param {param!r} not found on decorated function {func!r}")
        @wraps(func)
        def _wrapper(*args, **kwargs):
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            param_value = bound_args.arguments[param]
            if param_value is not default:
                return func(*args, **kwargs)
            def _multilambda_decorator(body):
                return func(*args, **{**kwargs, param: body})
            return _multilambda_decorator
        return _wrapper
    return _decorator
