import uasyncio
import sys

from .core import ASink


class AWrite(ASink):

    def __init__(self, stream=sys.stdout):
        self.stream = uasyncio.StreamWriter(stream)

    async def __call__(self, value):
        self.stream.write(value)
        await self.stream.drain()
