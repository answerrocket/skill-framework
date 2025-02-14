import functools


def flexible_decorator(func):
    """
    This is a decorator decorator to make all of these work:
    @decorator
    @decorator()
    @decorator(some_arg)
    @decorator(some_kw_arg=value)
    @decorator(some_arg, some_kw_arg=value)
    but it will only work for decorators that wrap functions.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if len(args) == 1 and callable(args[0]) and len(kwargs) == 0:
            return func(args[0])
        else:
            return lambda f: func(f, *args, **kwargs)
    return wrapper
