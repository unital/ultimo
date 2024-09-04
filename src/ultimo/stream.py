# SPDX-FileCopyrightText: 2024-present Unital Software <info@unital.dev>
#
# SPDX-License-Identifier: MIT

import sys

import uasyncio

from .core import ASink, ASource


class StreamMixin:
    """Mixin that gives async context manager behaviour to close a stream."""

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        await self.close()
        return False

    async def close(self):
        """Close the output stream."""
        await self.stream.wait_close()


class AWrite(ASink, StreamMixin):
    """Write to a stream asynchronously."""

    def __init__(self, stream=sys.stdout, source=None):
        super().__init__(source)
        self.stream = uasyncio.StreamWriter(stream)

    async def process(self, source_value):
        """Write data to the stream and drain."""
        self.stream.write(source_value)
        await self.stream.drain()


class ARead(ASource, StreamMixin):
    """Read from a stream asynchronously one character at a time."""

    def __init__(self, stream=sys.stdin):
        self.stream = uasyncio.StreamReader(stream)

    async def __call__(self):
        value = await self.stream.read(1)
        if value == "":
            return None
        return value
