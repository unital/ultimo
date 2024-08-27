from .core import EventSource

class Value(EventSource):
    """A class which stores a varying value that can be observed."""

    def __init__(self, value=None):
        super().__init__()
        self.value = value

    async def update(self, value):
        if value != self.value:
            self.value = value
            await self.fire()

    async def __call__(self, value=None):
        if value is not None:
            await self.update(value)
        return self.value
