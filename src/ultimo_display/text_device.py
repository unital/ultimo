# SPDX-FileCopyrightText: 2024-present Unital Software <info@unital.dev>
#
# SPDX-License-Identifier: MIT

"""Abstract base-class for text-based displays."""

from ultimo.core import Consumer

class ATextDevice:

    size: tuple[int, int]

    async def display_at(self, text: str, position: tuple[int, int]):
        raise NotImplementedError()

    async def erase(self, length: int, position: tuple[int, int]):
        await self.display_at(" "*length, position)

    async def set_cursor(self, position: tuple[int, int]):
        raise NotImplementedError()

    async def clear_cursor(self):
        raise NotImplementedError()

    async def clear(self):
        raise NotImplementedError()

    def display_text(self, row: int, column: int):
        return Consumer(self.display_at, ((column, row),))
