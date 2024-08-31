"""Polling source classes and decorators."""

import uasyncio

from .core import AFlow, ASource, asynchronize


class PollFlow(AFlow):
    """Iterator for Poll sources"""

    async def __anext__(self):
        await uasyncio.sleep(self.source.interval)
        return await self.source()


class Poll(ASource):
    """Source that calls a callback periodically."""

    flow = PollFlow

    def __init__(self, callback, interval):
        self.coroutine = asynchronize(callback)
        self.interval = interval

    async def __call__(self, value=None):
        return await self.coroutine()


def poll(callback):
    """Decorator that creates a Poll source from a callback."""

    def decorator(interval):
        return Poll(callback, interval)

    return decorator



