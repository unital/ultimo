# SPDX-FileCopyrightText: 2024-present Unital Software <info@unital.dev>
#
# SPDX-License-Identifier: MIT

"""Event-based sources that hold state."""

import uasyncio
import utime
from typing import Any, Callable, SupportsFloat


from .core import Consumer, EventSource, ASource, Returned
from .interpolate import linear


class Value(EventSource[Returned]):
    """A source which stores a varying value that can be observed.

    Note that iterators on a value will emit the value at the time when it
    runs, not at the time when the update occurred.  If the value updates
    rapidly then values may be skipped by the iterator.
    """

    value: Returned | None

    def __init__(self, value: Returned | None = None): ...

    async def update(self, value: Returned):
        """Update the value, firing the event."""

    async def __call__(self, value: Returned | None = None) -> Returned: ...

    def sink(self, source: ASource[Returned]) -> Consumer[Returned]:
        """Sink creator that updates the value from another source."""

    def __ror__(self, other: ASource[Returned]) -> Consumer[Returned]: ...


class EasedValue(Value[Returned]):
    """A Value that gradually changes to a target when updated."""

    #: The time taken to perform the easing.
    delay: float

    #: The time between easing updates in seconds.
    rate: float

    #: A callback to compute the value at a particular moment.
    easing: Callable[[Returned, Returned, SupportsFloat], Returned]

    #: The current target value being eased towards.
    target_value: Returned

    #: The current initial value being eased from.
    initial_value: Returned

    #: The time of the last change.
    last_change: float

    #: The asyncio task performing the easing updates, or None.
    easing_task: uasyncio.Task | None

    def __init__(
            self,
            value: Returned | None = None,
            easing: Callable[[Returned, Returned, float], Returned] = linear,
            delay: float = 1,
            rate: float = 0.05,
        ): ...

    async def ease(self):
        """Asyncronously ease the value to the target value."""

    async def update(self, value: Returned):
        """Update the target value, starting the easing task if needed."""


class Hold(Value[Returned]):
    """A value that holds a new value for a period, and then resets to a default."""

    #: The current target value being eased towards.
    default_value: Returned

    #: The time in seconds to hold the value before resetting to the default.
    hold_time: float

    #: The asyncio task performing the hold update, or None.
    hold_task: uasyncio.Task | None

    def __init__(self, value: Returned | None, hold_time: float = 60.0): ...

    async def hold(self) -> None:
        """Asynchronously wait for the hold time to expire and fire update."""

    async def update(self, value: Returned) -> None:
        """Update the value and start the hold task if needed."""
