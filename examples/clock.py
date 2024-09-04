""" Clock Example
"""

import uasyncio
from machine import RTC

from ultimo.pipelines import pipe
from ultimo.core import connect
from ultimo.poll import Poll
from ultimo.value import Value

@pipe
def hour(dt):
    return dt[4]

@pipe
def minute(dt):
    return dt[5]

@pipe
def second(dt):
    return dt[6]

async def main():
    """Poll values from the temperature sensor and print values as they change."""
    rtc = Poll(RTC().datetime, 0.1)
    clock = Value(await rtc())
    clock_sink = rtc | clock.sink()
    update_clock = uasyncio.create_task(clock_sink.run())
    print_hours = uasyncio.create_task(connect(clock | hour(), print))
    print_minutes = uasyncio.create_task(connect(clock | minute(), print))
    print_seconds = uasyncio.create_task(connect(clock | second(), print))
    await uasyncio.gather(update_clock, print_hours, print_minutes, print_seconds)


if __name__ == '__main__':
    # run forever
    uasyncio.run(main())

