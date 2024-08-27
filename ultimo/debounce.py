import asyncio
import utime

from .core import APipeline


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

