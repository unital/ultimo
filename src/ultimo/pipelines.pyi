# SPDX-FileCopyrightText: 2024-present Unital Software <info@unital.dev>
#
# SPDX-License-Identifier: MIT

"""Core pipeline classes for common operations"""

from typing import Any, Callable, Self, Coroutine, Concatenate, SupportsFloat

from ultimo.core import (
    AFlow,
    APipeline,
    APipelineFlow,
    ASource,
    Consumed,
    P,
    Returned,
    asynchronize,
)
from ultimo.interpolate import linear

class Apply(APipeline[Returned, Consumed]):
    """Pipeline that applies a callable to each value."""

    coroutine: Callable[[Consumed], Coroutine[Any, Any, Returned]]

    args: tuple[Any, ...]

    kwargs: dict[str, Any]

    def __init__(
        self,
        coroutine: Callable[[Consumed], Coroutine[Any, Any, Returned]],
        args: tuple[Any, ...] = (),
        kwargs: dict[str, Any] = {},
        source: ASource[Consumed] | None = None,
    ): ...

    def __ror__(self, other: ASource[Consumed]) -> Apply[Returned, Consumed]: ...

class Filter(APipeline[Returned, Returned]):
    """Pipeline that filters values."""

    filter: Callable[[Returned], Coroutine[Any, Any, bool]]

    args: tuple[Any, ...]

    kwargs: dict[str, Any]

    def __init__(
        self,
        filter: Callable[[Returned], Coroutine[Any, Any, bool]],
        args: tuple[Any, ...] = (),
        kwargs: dict[str, Any] = {},
        source: ASource[Returned] | None = None,
    ): ...

    def __ror__(self, other: ASource[Returned]) -> Filter[Returned]: ...

class Debounce(APipeline[Returned, Returned]):
    """Pipeline that stabilizes values emitted during a delay."""

    #: The debounce delay in millseconds.
    delay: float

    #: The millisecond ticks of the last change.
    last_change: int

    #: The value to return when debouncing.
    value: Returned | None

    def __init__(
        self, delay: float = 0.01, source: ASource[Returned] | None = None
    ): ...

    def __ror__(self, other: ASource[Returned]) -> Debounce[Returned]: ...

class DedupFlow(APipelineFlow[Returned, Returned]):

    flow: AFlow[Returned]

    #: The last value seen.
    value: Returned | None


class Dedup(APipeline[Returned, Returned]):
    """Pipeline that ignores repeated values."""

    def __ror__(self, other: ASource[Returned]) -> Dedup[Returned]: ...

class EWMA(APipeline[float, float]):
    """Pipeline that smoothes values with an exponentially weighted moving average."""

    #: The weight to apply to the new value.
    weight: float

    #: The previous weighted value.
    value: float

    def __init__(
        self, weight: float = 0.5, source: ASource[float] | None = None
    ): ...

    def __ror__(self, other: ASource[float]) -> Self: ...

def pipe(
    fn: Callable[Concatenate[Consumed, P], Returned]
) -> Callable[P, Apply[Returned, Consumed]]: ...

def apipe(
    fn: Callable[Concatenate[Consumed, P], Coroutine[Any, Any, Returned]]
) -> Callable[P, Apply[Returned, Consumed]]: ...

def filter(
    fn: Callable[Concatenate[Returned, P], bool]
) -> Callable[P, Filter[Returned]]: ...

def afilter(
    fn: Callable[Concatenate[Returned, P], Coroutine[Any, Any, bool]]
) -> Callable[P, Filter[Returned]]: ...
