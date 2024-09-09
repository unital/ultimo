# SPDX-FileCopyrightText: 2024-present Unital Software <info@unital.dev>
#
# SPDX-License-Identifier: MIT

from machine import RTC, Timer
from typing import Self

from ultimo.core import ThreadSafeSource
from ultimo.poll import Poll


class PollRTC(Poll[tuple[int, ...]]):
    """Poll the value of a real-time clock periodically."""

    rtc: RTC

    def __init__(self, rtc_id: int = 0, datetime: tuple[int, ...] | None = None, interval: float = 0.01): ...


class TimerInterrupt(ThreadSafeSource[bool]):
    """Schedule an timer-based interrupt source.

    The class acts as a context manager to set-up and remove the IRQ handler.
    """

    mode: int

    period: float

    timer: Timer

    def __init__(self, timer_id:int, mode: int = Timer.PERIODIC, freq: float = -1, period: float = -1): ...

    async def __aenter__(self) -> Self: ...

    async def __aexit__(self, *args): ...

    async def __call__(self) -> bool: ...

    async def close(self) -> None:
        """Stop the timer."""
