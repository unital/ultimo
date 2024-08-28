""" Potentiometer Example

This example shows how to take a noisy data source and produce a
clean sequence of values.  This was written for the Raspberry Pi
Pico, which has a fairly noisy onboard ADC.
"""

import asyncio
from machine import ADC, Pin

from ultimo.pipelines import pipe, Dedup
from ultimo.core import connect
from ultimo.poll import Poll


@pipe
def u16_to_u8(value):
    """Denoise uint16 values to uint8 with 6 significant bits."""
    return (value >> 8) & 0xfc


async def main(pin):
    """Poll values from a potentiometer and print values as they change."""
    potentiometer = ADC(pin)
    level = Poll(potentiometer.read_u16, 0.1) | u16_to_u8() | Dedup()
    task = asyncio.create_task(connect(level, print))
    await asyncio.gather(task)


if __name__ == '__main__':
    # run forever
    asyncio.run(main(Pin(26)))
