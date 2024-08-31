"""Core classes and helper functions for the Ultimo framework"""

from typing import Any, Callable, Self, Generic, TypeVar, AsyncIterator, ParamSpec, Coroutine, TypeAlias
import inspect
import uasyncio



Returned = TypeVar("Returned")
Consumed = TypeVar("Consumed")
P = ParamSpec("P")
Func = Callable[P, Returned]
Async = Callable[P, Coroutine[Any, Any, Returned]]


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

    async def __call__(self) -> Returned:
        """Get the source's current value."""
        raise NotImplementedError()

    def __aiter__(self) -> AFlow[Returned]:
        """Return an iterator for the source."""
        return self.flow(self)

    def __or__(self, other: "ASink[Returned]") -> Self: ...


class ASink(Generic[Consumed]):
    """Base class for consumers of sources."""

    def __init__(self, source: ASource[Consumed] | None = None): ...

    async def __call__(self, value: Consumed): ...

    def __ror__(self, other: ASource[Consumed]) -> Self: ...


class EventFlow(AFlow[Returned]):
    """Flow which awaits an Event and then gets the source value."""

    #: The source that created the flow.
    source: "EventSource[Returned]"


class EventSource(ASource[Returned]):
    """Base class for event-driven sources."""

    flow: type[EventFlow[Returned]] = EventFlow

    #: An asyncio Event which is set to wake the iterators.
    event: uasyncio.Event

    async def fire(self):
        """Set the async event to wake iterators."""


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

    def __ror__(self, other: ASource[Consumed]) -> Self: ...

def aiter(iterable) -> AsyncIterator:
    """Return an asynchronous iterator for an object."""
    return iterable.__aiter__()


async def anext(iterator: AsyncIterator[Returned]) -> Returned:
    """Return the net item from an asynchronous iterator."""
    return await iterator.__anext__()


def asynchronize(f: Func | Async) -> Async:
    """Ensure callable is asynchronous."""


async def connect(source: ASource[Returned], sink: Callable[[Returned], Any]):
    """Connect a sink to consume a source."""


async def aconnect(source: ASource[Returned], sink: Callable[[Returned], Coroutine[Any, Any, Any]]):
    """Connect an asynchronous sink to consume a source."""
    value = await source()
    await sink(value)
    async for value in source:
        await sink(value)
