# SPDX-FileCopyrightText: 2024-present Unital Software <info@unital.dev>
#
# SPDX-License-Identifier: MIT

"""Sources that depend on time-related functionality."""

from machine import RTC, Timer

from ultimo.core import ThreadSafeSource, asynchronize
from ultimo.poll import Poll


class PollRTC(Poll):
    """Poll the value of a real-time clock periodically."""

    def __init__(self, rtc_id=None, datetime=None, interval=0.01):
        if datetime is not None and rtc_id is not None:
            self.rtc = RTC(rtc_id, *datetime)
        elif rtc_id is not None:
            self.rtc = RTC(rtc_id)
        else:
            self.rtc = RTC()
        super().__init__(asynchronize(self.rtc.datetime), interval)


class TimerInterrupt(ThreadSafeSource):
    """Schedule an timer-based interrupt source.

    The class acts as a context manager to set-up and remove the IRQ handler.
    """

    def __init__(self, timer_id, mode=Timer.PERIODIC, freq=-1, period=-1):
        super().__init__()
        self.timer = Timer(timer_id)
        self.mode = mode
        if freq == -1:
            self.period = period
        else:
            self.period = 1.0/freq

    async def __aenter__(self):
        set_flag = self.event.set

        def isr(_):
            set_flag()

        self.timer.init(mode=self.mode, period=int(1000 * self.period), callback=isr)
        return self

    async def __aexit__(self, *args, **kwargs):
        await self.close()
        return False

    async def __call__(self):
        return True

    async def close(self):
        """Stop the timer."""
        self.timer.deinit()

