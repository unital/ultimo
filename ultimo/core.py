"""Core classes and helper functions for async iterators."""

import asyncio

def aiter(iterable):
    """Return an asynchronous iterator for an object."""
    return iterable.__aiter__()


async def anext(iterator):
    """Return the net item from an asynchronous iterator."""
    return await iterator.__anext__()


class AFlow:
    """Base class for iterators over sources."""

    def __init__(self, source):
        self.source = source

    def __aiter__(self):
        return self

    async def __anext__(self):
        raise NotImplementedError()


class ASource:
    """Base class for asynchronous sources."""

    async def __call__(self):
        raise NotImplementedError()

    def __aiter__(self):
        return self.flow(self)


class ASink:
    """Base class for consumers of sources."""

    def __init__(self, source=None):
        self.source = source

    async def __call__(self, value):
        # default do-nothing implementation, subclases should override
        pass

    def __ror__(self, other):
        if isinstance(other, ASource):
            self.source = other
            return self


class EventFlow(AFlow):
    async def __anext__(self):
        await self.source.event.wait()
        self.source.event.clear()
        return await self.source()


class EventSource(ASource):
    """Base class for event-driven sources."""

    flow = EventFlow

    def __init__(self):
        self.event = asyncio.Event()

    async def fire(self):
        self.event.set()
        await asyncio.sleep(0.0)
        self.event.clear()


class APipelineFlow(AFlow):
    """Base class for iterators over pipeline sources."""

    def __init__(self, source):
        super().__init__(source)
        self.flow = aiter(self.source.source)

    async def __anext__(self):
        # default implementation: apply source to value, skip None
        async for source_value in self.flow:
            if (value := await self.source(source_value)) is not None:
                return value


class APipeline(ASource, ASink):
    """Base class for combined source/sink objects."""

    flow = APipelineFlow

    async def __call__(self, value=None):
        # default do-nothing implementation, subclases may override
        if value is None:
            value = await self.source()

        return value

    def __ror__(self, other):
        if isinstance(other, ASource):
            self.source = other
            return self
        return NotImplemented

Generator = type(anext)

def asynchronize(f):
    """Ensure callable is asynchronous."""

    if isinstance(f, Generator):
        return f

    async def af(*args, **kwargs):
        return f(*args, **kwargs)

    return af


async def connect(source, sink):
    """Connect a sink to consume a source."""
    sink = asynchronize(sink)
    value = await source()
    await sink(value)
    async for value in source:
        await sink(value)


async def aconnect(source, sink):
    """Connect a sink to consume a source."""
    value = await source()
    await sink(value)
    async for value in source:
        await sink(value)
