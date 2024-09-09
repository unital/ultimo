""" Polled Button Example

This example shows how to debounce a noisy digital I/O.
"""

import uasyncio
from machine import Pin

from ultimo.pipelines import Debounce, Dedup
from ultimo.core import connect
from ultimo_machine.gpio import PollSignal


async def main(pin_id):
    """Poll values from a button and send an event when the button is pressed."""
    pin_source = PollSignal(pin_id, Pin.PULL_UP, interval=0.1)
    level = pin_source | Debounce() | Dedup()
    task = uasyncio.create_task(connect(level, print))
    await uasyncio.gather(task)


if __name__ == '__main__':
    # run forever
    uasyncio.run(main(19))
