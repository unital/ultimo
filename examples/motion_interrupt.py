"""Motion Sensor Interrupt Example

This example shows how to use an IRQ to feed a source.
"""

import uasyncio
from machine import Pin, RTC
import time

from ultimo.pipelines import pipe
from ultimo.core import connect, aconnect, EventSource
from ultimo.value import Hold


class Interrupt(EventSource):

    def __init__(self, pin, trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING):
        self.event = uasyncio.ThreadSafeFlag()
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


def report(value):
    print(value, RTC().datetime())

async def main(pin):
    """Wait for a motion sensor to trigger and print output."""
    async with Interrupt(pin) as motion:
        delay = Hold(0)
        task_1 = uasyncio.create_task(aconnect(motion, delay))
        task_2 = uasyncio.create_task(connect(delay, report))
        await uasyncio.gather(task_1, task_2)


if __name__ == '__main__':
    # run forever
    uasyncio.run(main(Pin(22, Pin.IN, Pin.PULL_DOWN)))




