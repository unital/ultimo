# SPDX-FileCopyrightText: 2024-present Unital Software <info@unital.dev>
#
# SPDX-License-Identifier: MIT

"""Core classes and helper functions for the Ultimo framework"""

import inspect
from typing import (
    Any,
    AsyncIterator,
    Callable,
    Concatenate,
    Coroutine,
    Generic,
    ParamSpec,
    Self,
    TypeAlias,
    TypeVar,
    overload
)

import uasyncio

Returned = TypeVar("Returned", covariant=True)
Consumed = TypeVar("Consumed", contravariant=True)
P = ParamSpec("P")

class AFlow(Generic[Returned]):
    """Base class for iterators over sources."""

    #: The source that created the flow.
    source: "ASource[Returned]"

    def __init__(self, source: "ASource[Returned]"): ...
    def __aiter__(self) -> Self:
        """Return the flow as its own iterator."""

    async def __anext__(self) -> Returned:
        """Get the next value.  Subclasses must override."""

class ASource(Generic[Returned]):
    """Base class for asynchronous sources."""

    #: The flow factory class variable used to create an iterator.
    flow: "type[AFlow]"

    async def __call__(self) -> Returned | None:
        """Get the source's current value."""

    def __aiter__(self) -> AFlow[Returned]:
        """Return an iterator for the source."""
        return self.flow(self)

class ASink(Generic[Consumed]):
    """Base class for consumers of sources."""

    def __init__(self, source: ASource[Consumed] | None = None): ...

    async def __call__(self, value: Consumed | None = None) -> Any:
        """Consume an input source value, or consume value from source."""

    async def _consume(self, value: Consumed) -> Any:
        """Consume an input source value."""

    async def run(self) -> None:
        """Consume the enitre source if available."""

    def create_task(self) -> uasyncio.Task:
        """Create a task that consumes the source."""

    def __ror__(self, other: ASource[Consumed]) -> ASink[Consumed]: ...


class Consumer(ASink[Consumed]):
    """A sink that wraps an asynchronous coroutine."""

    def __init__(
            self,
            consumer: Callable[Concatenate[Consumed, P], Coroutine[Any, Any, None]],
            args: tuple[Any, ...] = (),
            kwargs: dict[str, Any] = {},
            source: ASource | None = None,
        ): ...

    async def process(self, value: Consumed) -> None: ...

class EventFlow(AFlow[Returned]):
    """Flow which awaits an Event and then gets the source value."""

    #: The source that created the flow.
    source: "EventSource[Returned] | ThreadSafeSource[Returned]"

class EventSource(ASource[Returned]):
    """Base class for event-driven sources."""

    flow: type[EventFlow[Returned]] = EventFlow

    #: An uasyncio Event which is set to wake the iterators.
    event: uasyncio.Event

    async def fire(self):
        """Set the async event to wake iterators."""

class ThreadSafeSource(EventSource[Returned]):
    """Base class for event-driven sources."""

    #: An uasyncio ThreadSafeSource which is set to wake the iterators.
    event: uasyncio.ThreadSafeSource

class APipelineFlow(AFlow[Returned], Generic[Returned, Consumed]):
    """Base class for iterators over pipeline sources."""

    source: "APipeline[Returned, Consumed]"

    def __init__(self, source: "APipeline[Returned, Consumed]"): ...
    async def __anext__(self) -> Returned: ...

class APipeline(ASource[Returned], ASink[Consumed]):
    """Base class for combined source/sink objects."""

    #: The flow factory class variable used to create an iterator.
    flow: type[APipelineFlow[Returned, Consumed]] = APipelineFlow

    #: The input source for the pipeline.
    source: "ASource | None"

    def __init__(self, source: ASource[Consumed] | None = None): ...
    async def __call__(self, value: Consumed | None = None) -> Returned:
        """Get the source's current value, or transform an input source value."""

    def __ror__(self, other: ASource[Consumed]) -> APipeline[Returned, Consumed]: ...

def aiter(iterable) -> AsyncIterator:
    """Return an asynchronous iterator for an object."""
    return iterable.__aiter__()

async def anext(iterator: AsyncIterator[Returned]) -> Returned:
    """Return the net item from an asynchronous iterator."""
    return await iterator.__anext__()

def asynchronize(f: Callable[P, Returned]) -> Callable[P, Coroutine[None, None, Returned]]:
    """Ensure callable is asynchronous."""

async def connect(source: ASource[Returned], sink: Callable[[Returned], Any]):
    """Connect a sink to consume a source."""

async def aconnect(
    source: ASource[Returned], sink: Callable[[Returned], Coroutine[Any, Any, Any]]
):
    """Connect an asynchronous sink to consume a source."""
    value = await source()
    await sink(value)
    async for value in source:
        await sink(value)

def asink(afn: Callable[Concatenate[Consumed, P], Coroutine[Any, Any, None]]) -> Callable[P, Consumer[Consumed]]:
    """Turn an asynchronous function into a sink."""

def sink(fn: Callable[Concatenate[Consumed, P], None]) -> Callable[P, Consumer[Consumed]]:
    """Turn a synchronous function into a sink."""
