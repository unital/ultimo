""" Polled Button Example

This example shows how to debounce a noisy digital I/O.
"""

import uasyncio
from machine import Pin

from ultimo.pipelines import pipe, Debounce, Dedup, Filter
from ultimo.core import connect, asynchronize
from ultimo.poll import Poll

@Filter
def button_pressed(value):
    """Filter out button-down states."""
    # Pin is pulled up, so pushed button has 0 value on pin.
    return value == 0


async def main(pin):
    """Poll values from a button and send an event when the button is pressed."""
    pin_source = Poll(asynchronize(pin), 0.1)
    level = pin_source | Debounce() | Dedup() | button_pressed
    task = uasyncio.create_task(connect(level, print))
    await uasyncio.gather(task)


if __name__ == '__main__':
    # run forever
    uasyncio.run(main(Pin(19, Pin.IN, Pin.PULL_UP)))

