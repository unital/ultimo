# SPDX-FileCopyrightText: 2024-present Unital Software <info@unital.dev>
#
# SPDX-License-Identifier: MIT

"""
Potentiometer-PWM LED
---------------------

This example shows how to take a noisy data source and produce a clean sequence
of values, as well as using that stream to control a pulse-width modulation
output.  This was written for the Raspberry Pi Pico, which has a fairly noisy
onboard ADC.

This example expects a potentiometer connected pin 26, and uses the Raspberry
Pi Pico on-board LED.  Adjust appropritely for other set-ups.
"""

import uasyncio
from machine import ADC, Pin

from ultimo.core import connect
from ultimo.pipelines import Dedup, pipe
from ultimo_machine.gpio import PollADC, PWMSink


@pipe
def denoise(value):
    """Denoise uint16 values to 6 significant bits."""
    return value & 0xFC00


async def main(potentiometer_pin, led_pin):
    """Poll from a potentiometer, print values and change brightness of LED."""
    level = PollADC(potentiometer_pin, 0.1) | denoise() | Dedup()
    print_level = uasyncio.create_task(connect(level, print))
    led_brightness = level | PWMSink(led_pin, 1000, 0)
    await uasyncio.gather(print_level, led_brightness.create_task())


if __name__ == "__main__":
    # Raspberry Pi Pico pin numbers
    ADC_PIN = 26
    ONBOARD_LED_PIN = 25

    # run forever
    uasyncio.run(main(ADC_PIN, ONBOARD_LED_PIN))
