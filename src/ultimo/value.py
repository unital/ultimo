# SPDX-FileCopyrightText: 2024-present Unital Software <info@unital.dev>
#
# SPDX-License-Identifier: MIT

"""Event-based sources that hold state."""

import uasyncio
import utime

from .core import EventSource, ASink
from .interpolate import linear


class Value(EventSource, ASink):
    """A source which stores a varying value that can be observed.

    Note that iterators on a value will emit the value at the time when it
    runs, not at the time when the update occurred.  If the value updates
    rapidly then values may be skipped by the iterator.
    """

    def __init__(self, value=None):
        super().__init__()
        self.value = value

    async def update(self, value):
        """Update the value, firing the event."""
        if value != self.value:
            self.value = value
            await self.fire()

    async def __call__(self, value=None):
        if value is not None:
            await self.update(value)
        return self.value


class EasedValue(Value):
    """A Value that gradually changes to a target when updated."""

    #: The time taken to perform the easing.
    delay: float

    #: The time between easing updates in seconds.
    rate: float

    #: A callback to compute the value at a particular moment.
    easing: "Callable[[Any, Any, float], Any]"

    #: The update rate in seconds

    def __init__(self, value=None, easing=linear, delay=1, rate=0.05):
        super().__init__(value)
        self.target_value = value
        self.last_change = utime.time()
        self.easing = easing
        self.delay = delay
        self.rate = rate
        self.easing_task = None

    async def ease(self):
        """Asyncronously ease the value to the target value."""
        while (delta := utime.time() - self.last_change) <= self.delay:
            self.value = self.easing(
                self.initial_value, self.target_value, delta / self.delay
            )
            await self.fire()
            await uasyncio.sleep(self.rate)

        self.value = self.target_value
        await self.fire()
        self.easing_task = None

    async def update(self, value):
        """Update the target value, starting the easing task if needed."""
        if value != self.target_value:
            self.initial_value = value
            self.last_change = utime.time()
            self.target_value = value
            if self.easing_task is None:
                self.easing_task = uasyncio.create_task(self.ease())


class Hold(Value):
    """A value that holds a new value for a period, and then resets to a default."""

    def __init__(self, value, hold_time=60):
        super().__init__(value)
        self.default_value = value
        self.hold_time = hold_time
        self.last_change = utime.time()
        self.hold_task = None

    async def hold(self):
        while (delta := utime.time() - self.last_change) <= self.hold_time:
            await uasyncio.sleep(delta)

        self.value = self.default_value
        await self.fire()

    async def update(self, value):
        self.last_change = utime.time()
        if self.value == self.default_value and value != self.value:
            self.value = value
            self.hold_task = uasyncio.create_task(self.hold())
            await self.fire()
        # otherwise ignore the change
