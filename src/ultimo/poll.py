# SPDX-FileCopyrightText: 2024-present Unital Software <info@unital.dev>
#
# SPDX-License-Identifier: MIT

"""Polling source classes and decorators."""

import uasyncio

from .core import AFlow, ASource, asynchronize


class PollFlow(AFlow):
    """Iterator for Poll sources"""

    async def __anext__(self):
        await uasyncio.sleep(self.source.interval)
        return await super().__anext__()


class Poll(ASource):
    """Source that calls a coroutine periodically."""

    flow = PollFlow

    def __init__(self, coroutine, interval):
        self.coroutine = coroutine
        self.interval = interval

    async def __call__(self):
        value = await self.coroutine()
        return value


def poll(callback):
    """Decorator that creates a Poll source from a callback."""

    def decorator(interval):
        return Poll(asynchronize(callback), interval)

    return decorator


def apoll(coroutine):
    """Decorator that creates a Poll source from a callback."""

    def decorator(interval):
        return Poll(coroutine, interval)

    return decorator
