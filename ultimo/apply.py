from .core import APipeline, asynchronize


class Apply(APipeline):
    """Pipeline that applies a callable to each value."""

    def __init__(self, fn, args=(), kwargs={}, source=None):
        super().__init__(source)
        self.coroutine = asynchronize(fn)
        self.args = args
        self.kwargs = kwargs

    async def __call__(self, value=None):
        value = await super().__call__(value)
        if value is not None:
            return await self.coroutine(value, *self.args, **self.kwargs)


def pipe(fn):

    def decorator(*args, **kwargs):
        return Apply(fn, args, kwargs)

    return decorator


