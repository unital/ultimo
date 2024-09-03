# SPDX-FileCopyrightText: 2024-present Unital Software <info@unital.dev>
#
# SPDX-License-Identifier: MIT

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
        if value is None:
            raise StopAsyncIteration()
        return value


class ASource:
    """Base class for asynchronous sources."""

    #: The flow factory class variable used to create an iterator.
    flow: "type[AFlow]" = AFlow

    async def __call__(self):
        """Get the source's current value."""
        return None

    def __aiter__(self):
        """Return an iterator for the source."""
        return self.flow(self)


class ASink:
    """Base class for consumers of sources."""

    #: The input source for the pipeline.
    source: "ASource | None"

    def __init__(self, source=None):
        self.source = source

    async def __call__(self, value=None):
        """Consume an input source value, or the entire source if no value given."""
        if value is None and self.source is not None:
            value = await self.source()
        if value is not None:
            await self._process(value)

    async def _process(self, value):
        # default implementation, subclasses should override
        pass

    async def run(self):
        """Consume the source if available."""
        if self.source is not None:
            try:
                async for value in self.source:
                    await self(value)
            except uasyncio.CancelledError:
                return

    def __ror__(self, other):
        if isinstance(other, ASource):
            self.source = other
            return self
        return NotImplemented


class EventFlow(AFlow):
    """Flow which awaits an Event and then gets the source value."""

    async def __anext__(self):
        await self.source.event.wait()
        return super().__anext__()


class EventSource(ASource):
    """Base class for event-driven sources."""

    flow = EventFlow

    #: An uasyncio Event which is set to wake the iterators.
    event: uasyncio.Event

    def __init__(self):
        self.event = uasyncio.Event()

    async def fire(self):
        """Set the async event to wake iterators."""
        self.event.set()
        self.event.clear()


class ThreadSafeSource(EventSource):
    """Base class for interrupt-driven sources."""

    #: An uasyncio ThreadSafeFlag which is set to wake the iterators.
    event: uasyncio.ThreadSafeFlag

    def __init__(self):
        self.event = uasyncio.ThreadSafeFlag()


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
        else:
            raise StopAsyncIteration()


class APipeline(ASource, ASink):
    """Base class for combined source/sink objects."""

    #: The flow factory class variable used to create an iterator.
    flow: "type[APipelineFlow]" = APipelineFlow

    async def __call__(self, value=None):
        """Transform an input source value."""
        # default do-nothing implementation, subclases may override
        if value is None and self.source is not None:
            value = await self.source()

        if value is not None:
            return await self._process(value)

    async def _process(self, value):
        return value


def aiter(iterable):
    """Return an asynchronous iterator for an object."""
    return iterable.__aiter__()


async def anext(iterator):
    """Return the net item from an asynchronous iterator."""
    return await iterator.__anext__()


def asynchronize(f):
    """Make a synchronous callback synchronouse."""

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
    try:
        value = await source()
        await sink(value)
        async for value in source:
            await sink(value)
    except uasyncio.CancelledError:
        return
