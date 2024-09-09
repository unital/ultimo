""" Potentiometer Example

This example shows how to take a noisy data source and produce a
clean sequence of values.  This was written for the Raspberry Pi
Pico, which has a fairly noisy onboard ADC.
"""

import uasyncio
from machine import ADC, Pin

from ultimo.pipelines import pipe, Dedup
from ultimo.core import connect
from ultimo_machine.gpio import PollADC, PWMSink


@pipe
def denoise(value):
    """Denoise uint16 values to 6 significant bits."""
    return value & 0xfc00


async def main(potentiometer_pin, led_pin):
    """Poll from a potentiometer, print values and change brightness of LED."""
    level = PollADC(potentiometer_pin, 0.1) | denoise() | Dedup()
    print_level = uasyncio.create_task(connect(level, print))
    led_brightness = level | PWMSink(led_pin, 1000, 0)
    await uasyncio.gather(print_level, led_brightness.create_task())


if __name__ == '__main__':
    # Raspberry Pi Pico pin numbers
    ADC_PIN = 26
    ONBOARD_LED_PIN = 25

    # run forever
    uasyncio.run(main(ADC_PIN, ONBOARD_LED_PIN))
