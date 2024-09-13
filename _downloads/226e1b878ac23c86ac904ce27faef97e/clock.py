# SPDX-FileCopyrightText: 2024-present Unital Software <info@unital.dev>
#
# SPDX-License-Identifier: MIT

"""
Simple Clock
------------

This example shows how to poll the real-time clock and how to use a Value
as a source for multiple pipelines.  Output is to stdout.

This should work with any hardware that supports :py:class:`machine.RTC`.
"""

import uasyncio
from machine import RTC

from ultimo.core import connect
from ultimo.pipelines import pipe
from ultimo.value import Value
from ultimo.stream import AWrite
from ultimo_machine.time import PollRTC

fields = {
    4: "Hour",
    5: "Minute",
    6: "Second",
}

@pipe
def get_str(dt: tuple[int, ...], index: int):
    return f"{fields[index]:s}: {dt[index]:02d}"


async def main():
    """Poll values from the real-time clock and print values as they change."""
    rtc = PollRTC()
    clock = Value(await rtc())
    output = AWrite()

    update_clock = rtc | clock

    display_hour = clock | get_str(4) | output
    display_minute = clock | get_str(5) | output
    display_second = clock | get_str(6) | output

    # run forever
    await uasyncio.gather(
        update_clock.create_task(),
        display_hour.create_task(),
        display_minute.create_task(),
        display_second.create_task(),
    )


if __name__ == "__main__":
    # run forever
    uasyncio.run(main())
