# SPDX-FileCopyrightText: 2024-present Unital Software <info@unital.dev>
#
# SPDX-License-Identifier: MIT

"""Core pipeline classes for common operations"""

import utime

from ultimo.core import APipeline, APipelineFlow, asynchronize
from ultimo.interpolate import linear


class Apply(APipeline):
    """Pipeline that applies a callable to each value."""

    def __init__(self, coroutine, args=(), kwargs={}, source=None):
        super().__init__(source)
        self.coroutine = coroutine
        self.args = args
        self.kwargs = kwargs

    async def process(self, value):
        return await self.coroutine(value, *self.args, **self.kwargs)


class Filter(APipeline):
    """Pipeline that filters values."""

    def __init__(self, filter, args=(), kwargs={}, source=None):
        super().__init__(source)
        self.filter = filter
        self.args = args
        self.kwargs = kwargs

    async def process(self, value):
        if await self.filter(value, *self.args, **self.kwargs):
            return value
        else:
            return None


class Debounce(APipeline):
    """Pipeline that stabilizes polled values emitted for a short time."""

    def __init__(self, delay=0.01, source=None):
        super().__init__(source)
        self.delay = delay * 1000
        self.last_change = None
        self.value = None

    async def __call__(self, value=None):
        if (
            self.last_change is None
            or utime.ticks_diff(utime.ticks_ms(), self.last_change) > self.delay
        ):
            self.value = await super().__call__(value)
            self.last_change = utime.ticks_ms()

        return self.value


class DedupFlow(APipelineFlow):
    def __init__(self, source):
        super().__init__(source)
        self.value = None

    async def __anext__(self):
        async for source_value in self.flow:
            if (value := await self.source(source_value)) is not None:
                if value is not None and self.value != value:
                    self.value = value
                    return value
        else:
            raise StopAsyncIteration()


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
        if value is None and self.source is not None:
            value = await self.source()
        if self.value is None:
            self.value = value
        else:
            self.value = linear(self.value, value, self.weight)
        return self.value


def apipe(afn):
    """Decorator that produces a pipeline from an async function."""

    def apply_factory(*args, **kwargs):
        return Apply(afn, args, kwargs)

    return apply_factory


def pipe(fn):
    """Decorator that produces a pipeline from a function."""
    return apipe(asynchronize(fn))


def afilter(afn):
    """Decorator that produces a filter from an async function."""

    def filter_factory(*args, **kwargs):
        return Filter(afn, args, kwargs)

    return filter_factory


def filter(fn):
    """Decorator that produces a filter from a function."""
    return afilter(asynchronize(fn))
