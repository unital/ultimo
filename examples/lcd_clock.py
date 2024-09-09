"""
16x2 LCD Clock Example
----------------------

This example shows how to poll the real-time clock and how to use a Value
as a source for multiple pipelines, a custom subclass of ATextDevice, and how
to write a simple async function that consumes a flow of values.
"""

import uasyncio
from machine import I2C, Pin

from ultimo.pipelines import apipe, pipe, Dedup
from ultimo.core import asink
from ultimo.value import Value, Hold
from ultimo_machine.time import PollRTC
from ultimo_display.text_device import ATextDevice

from devices.lcd1602 import LCD1602_RGB

class HD44780TextDevice(ATextDevice):
    """Text devive for HD44780-style lcds."""

    size: tuple[int, int]

    def __init__(self, device):
        self.size = device._size
        self.device = device

    async def display_at(self, text: str, position: tuple[int, int]):
        # need proper lookup table for Unicode -> JIS X 0201 Hitachi variant
        self.device.write_ddram(position, text.encode())

    async def erase(self, length: int, position: tuple[int, int]):
        await self.display_at(" "*length, position)

    async def set_cursor(self, position: tuple[int, int]):
        # doesn't handle 4-line displays
        self.device.cursor = position
        self.device.cursor_on = True

    async def clear_cursor(self):
        self.device.cursor_off = True

    async def clear(self):
        self.device.cursor_off = True
        self.device.clear()


@apipe
async def get_formatted(dt: tuple[int, ...], index: int):
    return f"{dt[index]:02d}"


async def blink_colons(clock: Value, text_device: ATextDevice, positions: list[tuple[int, int]]):
    async for value in clock:
        for position in positions:
            await text_device.display_at(":", position)
        await uasyncio.sleep(0.8)
        for position in positions:
            await text_device.erase(1, position)


async def main(i2c):
    """Poll values from the real-time clock and print values as they change."""

    rgb1602 = LCD1602_RGB(i2c)
    await rgb1602.ainit()
    rgb1602.led_white()
    rgb1602.lcd.display_on = True

    text_device = HD44780TextDevice(rgb1602.lcd)

    rtc = PollRTC()
    clock = Value(await rtc())
    update_clock = (rtc | clock)
    display_hours = (clock | get_formatted(4) | Dedup() | text_device.display_text(0, 0))
    display_minutes = (clock | get_formatted(5) | Dedup() | text_device.display_text(0, 3))
    display_seconds = (clock | get_formatted(6) | Dedup() | text_device.display_text(0, 6))
    blink_display = blink_colons(clock, text_device, [(2, 0), (5, 0)])

    # run forever
    await uasyncio.gather(
        update_clock.create_task(),
        display_hours.create_task(),
        display_minutes.create_task(),
        display_seconds.create_task(),
        uasyncio.create_task(blink_display),
    )


if __name__ == '__main__':
    SDA = Pin(4)
    SCL = Pin(5)

    i2c = I2C(0, sda=SDA, scl=SCL, freq=400000)

    # run forever
    uasyncio.run(main(i2c))
