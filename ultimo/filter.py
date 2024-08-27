from .core import asynchronize, APipeline


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
