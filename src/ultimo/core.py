"""Core classes and helper functions for the Ultimo framework"""

import uasyncio


class AFlow:
    """Base class for iterators over sources."""

    #: The source that created the flow.
    source: "ASource"

    def __init__(self, source: "ASource"):
        self.source = source

    def __aiter__(self):
        """Return the flow as its own iterator."""
        return self

    async def __anext__(self):
        """Get the next value.  Subclasses must override."""
        value = await self.source()
        return value


class ASource:
    """Base class for asynchronous sources."""

    #: The flow factory class variable used to create an iterator.
    flow: "type[AFlow]"

    def get(self):

    async def __call__(self):
        """Get the source's current value."""
        raise NotImplementedError()

    def __aiter__(self):
        """Return an iterator for the source."""
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
    """Flow which awaits an Event and then gets the source value."""

    async def __anext__(self):
        await self.source.event.wait()
        self.source.event.clear()
        return await self.source()


class EventSource(ASource):
    """Base class for event-driven sources."""

    flow = EventFlow

    #: An asyncio Event which is set to wake the iterators.
    event: uasyncio.Event

    def __init__(self):
        self.event = uasyncio.Event()

    async def fire(self):
        """Set the async event to wake iterators."""
        self.event.set()
        await uasyncio.sleep(0.0)
        self.event.clear()


class APipelineFlow(AFlow):
    """Base class for iterators over pipeline sources."""

    source: "APipeline"

    def __init__(self, source: "APipeline"):
        super().__init__(source)
        self.flow = aiter(self.source.source)

    async def __anext__(self):
        # default implementation: apply source to value, skip None
        async for source_value in self.flow:
            if (value := await self.source(source_value)) is not None:
                return value


class APipeline(ASource, ASink):
    """Base class for combined source/sink objects."""

    #: The flow factory class variable used to create an iterator.
    flow: "type[APipelineFlow]" = APipelineFlow

    #: The input source for the pipeline.
    source: "ASource | None"

    def __init__(self, source: "ASource | None" = None):
        self.source = source

    async def __call__(self, value=None):
        """Get the source's current value, or transform an input source value."""
        # default do-nothing implementation, subclases may override
        if value is None:
            value = await self.source()

        return value

    def __ror__(self, other):
        if isinstance(other, ASource):
            self.source = other
            return self
        return NotImplemented

_Generator = type(anext)

def aiter(iterable):
    """Return an asynchronous iterator for an object."""
    return iterable.__aiter__()


async def anext(iterator):
    """Return the net item from an asynchronous iterator."""
    return await iterator.__anext__()


def asynchronize(f):
    """Ensure callable is asynchronous."""

    if isinstance(f, _Generator):
        return f

    async def af(*args, **kwargs):
        return f(*args, **kwargs)

    return af


async def connect(source, sink):
    """Connect a sink to consume a source."""
    asink = asynchronize(sink)
    value = await source()
    await asink(value)
    async for value in source:
        await asink(value)


async def aconnect(source, sink):
    """Connect a sink to consume a source."""
    value = await source()
    await sink(value)
    async for value in source:
        await sink(value)
