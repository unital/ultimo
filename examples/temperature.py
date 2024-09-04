""" Temperature Example

This example shows how to smooth data from a source to produce a
clean sequence of values.  This was written for the Raspberry Pi
Pico's onboard temperature sensor.

This shows how to use the Poll, EWMA, pipe and connect functions.
"""

import uasyncio
from machine import ADC
import sys

from ultimo.pipelines import pipe, EWMA, Apply
from ultimo.core import aconnect, ASink
from ultimo.poll import Poll
from ultimo.stream import AWrite


@pipe
def u16_to_celcius(value: int) -> float:
    """Convert raw uint16 values to temperatures."""
    return 27 - (3.3 * value / 0xffff - 0.706) / 0.001721


async def main():
    """Poll values from the temperature sensor and print values as they change."""
    adc = ADC(ADC.CORE_TEMP)

    temperature = Poll(adc.read_u16, 1) | u16_to_celcius() | EWMA(0.05)
    task = uasyncio.create_task(aconnect(temperature | Apply("{}\n".format), AWrite()))
    await uasyncio.gather(task)


if __name__ == '__main__':
    # run forever
    uasyncio.run(main())

