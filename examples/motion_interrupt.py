"""Motion Sensor Interrupt Example

This example shows how to use an IRQ to feed a ThreadSafeSource source, the
Hold source, how to connect to a value's sink,  and using the consumer
decorator.
"""

import uasyncio
from machine import Pin, RTC

from ultimo.core import sink
from ultimo.value import Hold
from ultimo_machine.gpio import PinInterrupt


@sink
def report(value):
    print(value, RTC().datetime())


async def main(pin_id):
    """Wait for a motion sensor to trigger and print output."""
    async with PinInterrupt(pin_id, Pin.PULL_DOWN) as motion_pin:
        activity = Hold(False)
        update_activity = motion_pin | activity
        report_activity = activity | report()

        update_task = uasyncio.create_task(update_activity.run())
        report_task = uasyncio.create_task(report_activity.run())
        await uasyncio.gather(update_task, report_task)


if __name__ == '__main__':
    # run forever
    uasyncio.run(main(22))
