from .core import APipeline


def interpolate(x, y, t):
    """Interpolate value between x and y."""
    return t * x + (1-t) * y


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
            self.value = interpolate(value, self.value, self.weight)
        return self.value

