"""Motion Sensor Interrupt Example

This example shows how to use an IRQ to feed a ThreadSafeSource source, the
Hold source, how to connect to a value's sink,  and using the consumer
decorator.
"""

import uasyncio
from machine import Pin, RTC

from ultimo.core import ThreadSafeSource, consumer
from ultimo.value import Hold


class IRQInterrupt(ThreadSafeSource):

    def __init__(self, pin, trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING):
        super().__init__()
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


@consumer
def report(value):
    print(value, RTC().datetime())


async def main(pin):
    """Wait for a motion sensor to trigger and print output."""
    async with IRQInterrupt(pin) as motion_pin:
        activity = Hold(0)
        update_activity = motion_pin | activity.sink()
        report_activity = activity | report()
        update_task = uasyncio.create_task(update_activity.run())
        report_task = uasyncio.create_task(report_activity.run())
        await uasyncio.gather(update_task, report_task)


if __name__ == '__main__':
    # run forever
    uasyncio.run(main(Pin(22, Pin.IN, Pin.PULL_DOWN)))
