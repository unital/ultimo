""" Clock Example
"""

import asyncio
from machine import RTC

from ultimo.apply import pipe
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
    task_1 = asyncio.create_task(connect(rtc, clock))
    task_2 = asyncio.create_task(connect(clock | hour(), print))
    task_3 = asyncio.create_task(connect(clock | minute(), print))
    task_4 = asyncio.create_task(connect(clock | second(), print))
    await asyncio.gather(task_1, task_2, task_3, task_4)


if __name__ == '__main__':
    # run forever
    asyncio.run(main())

