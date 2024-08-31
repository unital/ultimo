"""Core pipeline classes for common operations"""

from ultimo.core import APipeline, APipelineFlow, asynchronize
from ultimo.interpolate import linear


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


class Filter(APipeline):
    """Pipeline that filters values."""

    def __init__(self, filter, source=None):
        super().__init__(source)
        self.filter = asynchronize(filter)

    async def __call__(self, value=None):
        value = await super().__call__(value)
        if await self.filter(value):
            return value
        else:
            return None


class Debounce(APipeline):
    """Pipeline that stabilizes values emitted during a delay."""

    def __init__(self, delay=0.01, source=None):
        super().__init__(source)
        self.delay = delay * 1000
        self.last_change = None
        self.value = None

    async def __call__(self, value=None):
        if self.last_change is None or utime.ticks_diff(utime.ticks_ms(), self.last_change) > self.delay:
            if value is None:
                value = await self.source()
            self.value = value
            self.last_change = utime.ticks_ms()

        return self.value


class DedupFlow(APipelineFlow):
    def __init__(self, source):
        super().__init__(source)
        self.value = None

    async def __anext__(self):
        async for value in self.flow:
            if self.value != value:
                break

        self.value = value
        return value


class Dedup(APipeline):
    """Pipeline that ignores repeated values."""

    flow = DedupFlow


class EWMA(APipeline):
    """Pipeline that smoothes values with an exponentially weighted moving average."""

    def __init__(self, weight=0.5, source=None):
        super().__init__(source)
        self.weight = weight
        self.value = None

    async def __call__(self, value=None):
        if value is None:
            value = await self.source()
        if self.value is None:
            self.value = value
        else:
            self.value = linear(self.value, value, self.weight)
        return self.value

def pipe(fn):

    def decorator(*args, **kwargs):
        return Apply(fn, args, kwargs)

    return decorator
