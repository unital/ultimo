# SPDX-FileCopyrightText: 2024-present Unital Software <info@unital.dev>
#
# SPDX-License-Identifier: MIT

"""ANSI-compatible text device."""

from ultimo.stream import AWrite
from ultimo_display.text_device import ATextDevice


class ANSITextDevice(ATextDevice):
    """Text device that outputs ANSI control codes."""

    stream: AWrite

    def __init__(self, stream=None, size=(80, 25)):
        if stream is None:
            stream = AWrite()
        self.stream = stream
        self.size = size

    async def display_at(self, text: str, position: tuple[int, int]):
        column, row = position
        await self.stream(f'\x1b[{row+1:d};{column+1:d}f' + text)

    async def set_cursor(self, position: tuple[int, int]):
        column, row = position
        await self.stream('\x1b[%d;%dH\x1b[?25h' % (row+1, column+1))

    async def clear_cursor(self):
        await self.stream('\x1b[?25l')

    async def clear(self):
        await self.stream('\x1b[2J')
