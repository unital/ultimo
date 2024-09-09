# SPDX-FileCopyrightText: 2024-present Unital Software <info@unital.dev>
#
# SPDX-License-Identifier: MIT

"""Driver for AiP31068L I2C controller for HD44780-style LCD displays"""

from machine import I2C

from .hd44780 import HD44780, FONT_5x8_DOTS

DEFAULT_ADDRESS = (0x7c>>1)


class AiP31068L(HD44780):
    """I2C controller for HD44780-style displays"""

    i2c: I2C

    address: int

    def __init__(self, i2c: I2C, address: int = DEFAULT_ADDRESS, size: tuple[int, int] = (16, 2), font: int = FONT_5x8_DOTS, track: bool = True):
        self.i2c = i2c
        self.address = address
        super().__init__(size, font, track)

    def _writeto_mem(self, control: int, data: int):
        self.i2c.writeto_mem(self.address, control, bytes([data]))
        super()._writeto_mem(control, data)
