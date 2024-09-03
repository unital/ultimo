# SPDX-FileCopyrightText: 2024-present Unital Software <info@unital.dev>
#
# SPDX-License-Identifier: MIT

import sys

import uasyncio

from .core import ASink, ASource


class AWrite(ASink):
    """Write to a stream asynchronously."""

    def __init__(self, stream=sys.stdout, source=None):
        super().__init__(source)
        self.stream = uasyncio.StreamWriter(stream)

    async def __call__(self, value=None):
        super().__call__(value)
        if value is not None:
            self.stream.write(value)
            await self.stream.drain()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        await self.close()
        return False

    async def close(self):
        """Close the output stream."""
        await self.stream.wait_close()


class ARead(ASource):
    """Read from a stream asynchronously one character at a time."""

    def __init__(self, stream=sys.stdin):
        self.stream = uasyncio.StreamReader(stream)

    async def __call__(self):
        value = await self.stream.read(1)
        if value == "":
            raise StopIteration()

        return value

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        await self.close()
        return False

    async def close(self):
        """Close the output stream."""
        await self.stream.wait_close()
