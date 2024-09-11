# SPDX-FileCopyrightText: 2024-present Unital Software <info@unital.dev>
#
# SPDX-License-Identifier: MIT

"""Concrete implementation of a text-based displays in a framebuffer."""

from framebuf import FrameBuffer

from .text_device import ATextDevice


class FrameBufferTextDevice(ATextDevice):

    buffer: bytearray

    def __init__(self, buffer: bytearray, size: tuple[int, int], format: int, background: int = 0, foreground: int = 1):
        self.buffer = buffer
        self.size = size
        width, height = size
        self.framebuf = FrameBuffer(buffer, width*8, height*8, format)
        self.foreground = foreground
        self.background = background

    async def display_at(self, text: str, position: tuple[int, int]):
        x, y = position
        self.framebuf.text(text, x*8, y*8, self.foreground)

    async def erase(self, length: int, position: tuple[int, int]):
        x, y = position
        self.framebuf.rect(x*8, y*8, length*8, 8, self.background, True)

    async def set_cursor(self, position: tuple[int, int]):
        x, y = position
        self.framebuf.hline(x*8, y*8, 8, self.foreground)

    async def clear_cursor(self, position: tuple[int, int]):
        x, y = position
        self.framebuf.hline(x*8, y*8, 8, self.background)

    async def clear(self):
        self.framebuf.fill(self.background)
