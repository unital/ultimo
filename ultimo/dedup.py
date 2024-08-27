from .core import APipeline, APipelineFlow


class DedupFlow(APipelineFlow):
    def __init__(self, source):
        super().__init__(source)
        self.value = None

    async def __anext__(self):
        async for value in self.flow:
            if self.value != value:
                break

        self.value = value
        return value


class Dedup(APipeline):
    """Pipeline that ignores repeated values."""

    flow = DedupFlow

