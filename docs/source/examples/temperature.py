# SPDX-FileCopyrightText: 2024-present Unital Software <info@unital.dev>
#
# SPDX-License-Identifier: MIT

"""
Temperature
-----------

This example shows how to smooth data from a source to produce a
clean sequence of values.  This was written for the Raspberry Pi
Pico's onboard temperature sensor.

This shows how to use the Poll, EWMA, the pipe decorator, and the
stream writer.
"""

import uasyncio
from machine import ADC

from ultimo.pipelines import EWMA, pipe
from ultimo.stream import AWrite
from ultimo_machine.gpio import PollADC


@pipe
def u16_to_celcius(value: int) -> float:
    """Convert raw uint16 values to temperatures."""
    return 27 - (3.3 * value / 0xFFFF - 0.706) / 0.001721


@pipe
def format(value: float) -> str:
    """Format a temperature for output."""
    return f"{value:.1f}°C\n"


async def main():
    """Poll values from the temperature sensor and print values as they change."""
    temperature = PollADC(ADC.CORE_TEMP, 1) | u16_to_celcius() | EWMA(0.05)
    write_temperature = temperature | format() | AWrite()
    await uasyncio.gather(write_temperature.create_task())


if __name__ == "__main__":
    # run forever
    uasyncio.run(main())
