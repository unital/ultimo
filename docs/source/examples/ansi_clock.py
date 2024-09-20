# SPDX-FileCopyrightText: 2024-present Unital Software <info@unital.dev>
#
# SPDX-License-Identifier: MIT

"""ANSI-compatible text device."""

import uasyncio

from ultimo.pipelines import Dedup, apipe
from ultimo.value import Value
from ultimo_display.ansi_text_device import ANSITextDevice
from ultimo_display.text_device import ATextDevice
from ultimo_machine.time import PollRTC


@apipe
async def get_formatted(dt: tuple[int, ...], index: int):
    return f"{dt[index]:02d}"


async def blink_colons(
    clock: Value, text_device: ATextDevice, positions: list[tuple[int, int]]
):
    async for value in clock:
        for position in positions:
            await text_device.display_at(":", position)
        await uasyncio.sleep(0.8)
        for position in positions:
            await text_device.erase(1, position)


async def main():
    """Poll values from the real-time clock and print values as they change."""

    text_device = ANSITextDevice()
    await text_device.clear()

    rtc = PollRTC()
    clock = Value(await rtc())
    update_clock = rtc | clock
    display_hours = clock | get_formatted(4) | Dedup() | text_device.display_text(0, 0)
    display_minutes = (
        clock | get_formatted(5) | Dedup() | text_device.display_text(0, 3)
    )
    display_seconds = (
        clock | get_formatted(6) | Dedup() | text_device.display_text(0, 6)
    )
    blink_display = blink_colons(clock, text_device, [(2, 0), (5, 0)])

    # run forever
    await uasyncio.gather(
        update_clock.create_task(),
        display_hours.create_task(),
        display_minutes.create_task(),
        display_seconds.create_task(),
        uasyncio.create_task(blink_display),
    )


if __name__ == "__main__":
    # run forever
    uasyncio.run(main())
