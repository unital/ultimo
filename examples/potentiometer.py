""" Potentiometer Example

This example shows how to take a noisy data source and produce a
clean sequence of values.  This was written for the Raspberry Pi
Pico, which has a fairly noisy onboard ADC.
"""

import uasyncio
from machine import ADC, Pin

from ultimo.pipelines import pipe, Dedup
from ultimo.core import connect
from ultimo_machine.adc import PollADC


@pipe
def u16_to_u8(value):
    """Denoise uint16 values to uint8 with 6 significant bits."""
    return (value >> 8) & 0xfc


async def main(pin):
    """Poll values from a potentiometer and print values as they change."""
    potentiometer = ADC(pin)
    level = PollADC(potentiometer, 0.1) | u16_to_u8() | Dedup()
    task = uasyncio.create_task(connect(level, print))
    await uasyncio.gather(task)


if __name__ == '__main__':
    # run forever
    uasyncio.run(main(Pin(26)))
