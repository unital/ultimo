""" Temperature Example

This example shows how to smooth data from a source to produce a
clean sequence of values.  This was written for the Raspberry Pi
Pico's onboard temperature sensor.

This shows how to use the Poll, EWMA, pipe and connect functions.
"""

import asyncio
from machine import ADC

from ultimo.pipelines import pipe, EWMA
from ultimo.core import connect
from ultimo.poll import Poll


@pipe
def u16_to_celcius(value):
    """Convert raw uint16 values to temperatures."""
    return 27 - (3.3 * value / 0xffff - 0.706) / 0.001721


async def main():
    """Poll values from the temperature sensor and print values as they change."""
    adc = ADC(ADC.CORE_TEMP)
    temperature = Poll(adc.read_u16, 1) | u16_to_celcius() | EWMA(0.05)
    task = asyncio.create_task(connect(temperature, print))
    await asyncio.gather(task)


if __name__ == '__main__':
    # run forever
    asyncio.run(main())

