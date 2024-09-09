""" Clock Example

This example shows how to poll the real-time clock and how to use a Value
as a source for multiple pipelines.
"""

import uasyncio
from machine import RTC

from ultimo.pipelines import pipe
from ultimo.core import connect
from ultimo.value import Value
from ultimo_machine.time import PollRTC

@pipe
def hour(dt: tuple[int, ...]):
    return dt[4]

@pipe
def minute(dt: tuple[int, ...]):
    return dt[5]

@pipe
def second(dt: tuple[int, ...]):
    return dt[6]

async def main():
    """Poll values from the real-time clock and print values as they change."""
    rtc = PollRTC()
    clock = Value(await rtc())
    update_clock = (rtc | clock).create_task()
    print_hours = uasyncio.create_task(connect(clock | hour(), print))
    print_minutes = uasyncio.create_task(connect(clock | minute(), print))
    print_seconds = uasyncio.create_task(connect(clock | second(), print))
    # run forever
    await uasyncio.gather(update_clock, print_hours, print_minutes, print_seconds)


if __name__ == '__main__':
    # run forever
    uasyncio.run(main())

