"""Motion Sensor Interrupt Example

This example shows how to use an IRQ to feed a source.
"""

import asyncio
from machine import Pin, RTC
import time

from ultimo.pipelines import pipe
from ultimo.core import connect, aconnect, EventSource
from ultimo.value import Value


class Interrupt(EventSource):

    def __init__(self, pin, trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING):
        self.event = asyncio.ThreadSafeFlag()
        self.pin = pin
        self.trigger = trigger

    async def __aenter__(self):
        set_flag = self.event.set

        def isr(_):
            set_flag()

        self.pin.irq(isr, self.trigger)

        return self

    async def __aexit__(self, *args, **kwargs):
        await self.close()
        return False

    async def __call__(self):
        return self.pin()

    async def close(self):
        self.pin.irq()


class DelayedShutoff(Value):

    def __init__(self, value=0, shutoff_delay=60):
        super().__init__(value)
        self.shutoff_delay = shutoff_delay
        self.last_change = time.time()
        self.delay_task = None

    async def delay_shutoff(self):
        while (delta := time.time() - self.last_change) <= self.shutoff_delay:
            await asyncio.sleep(delta)

        self.value = 0
        await self.fire()

    async def update(self, value):
        self.last_change = time.time()
        if value == 1 and self.value == 0:
            self.value = value
            self.delay_task = asyncio.create_task(self.delay_shutoff())
            await self.fire()


def report(value):
    print(value, RTC().datetime())

async def main(pin):
    """Wait for a motion sensor to trigger and print output."""
    async with Interrupt(pin) as motion:
        delay = DelayedShutoff()
        task_1 = asyncio.create_task(aconnect(motion, delay))
        task_2 = asyncio.create_task(connect(delay, report))
        await asyncio.gather(task_1, task_2)


if __name__ == '__main__':
    # run forever
    asyncio.run(main(Pin(22, Pin.IN, Pin.PULL_DOWN)))




