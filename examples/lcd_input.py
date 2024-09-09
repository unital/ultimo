"""
16x2 LCD Python Eval
--------------------

This example shows how to handle text input from a serial port and display it
on a 16x2 LCD panel, and implements a simple Python eval-based calculator.
This uses an async function to handle the state of editing a line, evaluating
the expression on return, and displaying the result.

For best results, use a terminal emulator or mpremote, rather than Thonny or
other line-based terminals.
"""

import uasyncio
from machine import I2C, Pin

from ultimo.pipelines import apipe, pipe, Dedup
from ultimo.core import asink
from ultimo.stream import ARead
from ultimo.value import Value, Hold
from ultimo_machine.time import PollRTC
from ultimo_display.text_device import ATextDevice

from devices.lcd1602 import LCD1602_RGB
from devices.hd44780_text_device import HD44780TextDevice


async def display_line(display, text, line=1):
    """Display a single line."""
    await display.display_at(f"{text:<16s}", (0, line))


async def display_lines(input, display):
    """Display result line and editing line in a display."""
    last_line = ""
    current_line = ""
    async for char in input:
        if char == '\n':
            try:
                last_line = str(eval(current_line))
            except Exception as exc:
                last_line = str(exc)
            current_line = ""
            await display_line(display, last_line[:16], 0)
        elif ord(char) == 127:
            # backspace
            current_line = current_line[:-1]
        elif ord(char) == 8:
            # tab
            current_line = current_line + " " * 4
        else:
            current_line += char
        await display_line(display, ("> " + current_line)[-16:], 1)


async def main(i2c):
    """Poll values from the real-time clock and print values as they change."""

    rgb1602 = LCD1602_RGB(i2c)
    await rgb1602.ainit()
    rgb1602.led_white()
    rgb1602.lcd.display_on = True
    rgb1602.lcd.cursor_on = True

    text_device = HD44780TextDevice(rgb1602.lcd)
    input = ARead()

    # run forever
    await uasyncio.gather(uasyncio.create_task(display_lines(input, text_device)))


if __name__ == '__main__':
    SDA = Pin(4)
    SCL = Pin(5)

    i2c = I2C(0, sda=SDA, scl=SCL, freq=400000)

    # run forever
    uasyncio.run(main(i2c))

