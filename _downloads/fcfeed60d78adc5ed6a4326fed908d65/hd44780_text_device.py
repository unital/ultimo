# SPDX-FileCopyrightText: 2024-present Unital Software <info@unital.dev>
#
# SPDX-License-Identifier: MIT

"""ATextDevice implementation for HD44780 LCD displays"""

from ultimo_display.text_device import ATextDevice


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
        await self.display_at(" " * length, position)

    async def set_cursor(self, position: tuple[int, int]):
        # doesn't handle 4-line displays
        self.device.cursor = position
        self.device.cursor_on = True

    async def clear_cursor(self):
        self.device.cursor_off = True

    async def clear(self):
        self.device.cursor_off = True
        self.device.clear()
