# SPDX-FileCopyrightText: 2024-present Unital Software <info@unital.dev>
#
# SPDX-License-Identifier: MIT

"""Core pipeline classes for common operations"""

from typing import Any, Callable, Self

from ultimo.core import (
    APipeline,
    APipelineFlow,
    ASource,
    Async,
    Consumed,
    Func,
    P,
    Returned,
    asynchronize,
)
from ultimo.interpolate import linear

class Apply(APipeline[Returned, Consumed]):
    """Pipeline that applies a callable to each value."""

    coroutine: Async

    def __init__(
        self,
        fn: Callable[[Consumed], Returned],
        args: tuple[Any, ...] = (),
        kwargs: dict[str, Any] = {},
        source: ASource[Consumed] | None = None,
    ): ...
    def __ror__(self, other: ASource[Consumed]) -> Self: ...

class Filter(APipeline[bool, Consumed]):
    """Pipeline that filters values."""

    def __init__(
        self, filter: Func | Async, source: ASource[Consumed] | None = None
    ): ...

class Debounce(APipeline[Returned, Returned]):
    """Pipeline that stabilizes values emitted during a delay."""

    def __init__(
        self, delay: float = 0.01, source: ASource[Returned] | None = None
    ): ...

class DedupFlow(APipelineFlow[Returned, Returned]): ...

class Dedup(APipeline[Returned, Returned]):
    """Pipeline that ignores repeated values."""

    flow: DedupFlow[Returned]

class EWMA(APipeline[Returned, Returned]):
    """Pipeline that smoothes values with an exponentially weighted moving average."""

    def __init__(
        self, weight: float = 0.5, source: ASource[Returned] | None = None
    ): ...

def pipe(
    fn: Callable[[Consumed], Returned]
) -> Callable[[], Apply[Returned, Consumed]]: ...
