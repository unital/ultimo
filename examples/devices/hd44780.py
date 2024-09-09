# SPDX-FileCopyrightText: 2024-present Unital Software <info@unital.dev>
#
# SPDX-License-Identifier: MIT

"""Driver for HD44780-style LCD displays"""

# Command
CLEAR_DISPLAY = 0x01
RETURN_HOME = 0x02
ENTRY_MODE_SET = 0x04
DISPLAY_CONTROL = 0x08
CURSOR_SHIFT = 0x10
FUNCTION_SET = 0x20
SET_CGRAM_ADDR = 0x40
SET_DDRAM_ADDR = 0x80

# Entry modes
CURSOR_RIGHT = 0x00
CURSOR_LEFT = 0x02
SHIFT_INCREMENT = 0x01
SHIFT_DECREMENT = 0x00

# Display
DISPLAY_ON = 0x04
DISPLAY_OFF = 0x00
CURSOR_ON = 0x02
CURSOR_OFF = 0x00
BLINK_ON = 0x01
BLINK_OFF = 0x00

# Display/cursor shift
DISPLAY_MOVE = 0x08
CURSOR_MOVE = 0x00
MOVE_RIGHT = 0x04
MOVE_LEFT = 0x00

# Function settings (must match hardware)
LINES_2 = 0x08
LINES_1 = 0x00
FONT_5x8_DOTS = 0x00
FONT_5x10_DOTS = 0x04

_DDRAM_BANK_SIZE = 40
_CGRAM_BANK_SIZE = 64


class HD44780_State:

    size: tuple[int, int]

    cgram_mode: bool | None = None

    cgram_address: int | None = None

    cgram: bytearray

    ddram_address: int | None = None

    ddram: tuple[bytearray, bytearray] | None = None

    entry_mode: int | None = None

    display_state: int | None = None

    function_settings: int | None = None

    shift: int | None = None

    def __init__(self, size: tuple[int, int] = (16, 2)):
        self.size = size
        self.cgram = bytearray(_CGRAM_BANK_SIZE)

    def _writeto_mem(self, control: int, data: int):
        if control == 0x40:
            self.write(data)
        elif control == 0x80:
            self.command(data)
        else:
            raise ValueError(f"Unknown control code {control:x}")

    def write(self, data: int):
        if self.cgram_mode is None:
            raise RuntimeError("Unsure whether writing to CGRAM or DDRAM")

        if self.cgram_mode:
            if self.cgram_address is None:
                raise RuntimeError("Writing at unknown CGRAM address")

            self.cgram[self.cgram_address] = data & 0b11111
            self.cgram_address = (self.cgram_address + 1) % _CGRAM_BANK_SIZE
        else:
            if self.ddram_address is None:
                raise RuntimeError("Writing at unknown DDRAM address")
            if self.ddram is None:
                raise RuntimeError("DDRAM state is unknown")
            column, row = self.cursor
            self.ddram[row][column] = data
            self.increment_ddram_address()

    def command(self, command: int):
        # note: order matters here due to the way bit-patterns work
        if command & SET_DDRAM_ADDR:
            self.set_ddram_addr(command & ~SET_DDRAM_ADDR)
        elif command & SET_CGRAM_ADDR:
            self.set_cgram_addr(command & ~SET_CGRAM_ADDR)
        elif command & FUNCTION_SET:
            self.function_set(command & ~FUNCTION_SET)
        elif command & CURSOR_SHIFT:
            self.cursor_shift(command & ~CURSOR_SHIFT)
        elif command & DISPLAY_CONTROL:
            self.display_control(command & ~DISPLAY_CONTROL)
        elif command & ENTRY_MODE_SET:
            self.entry_mode_set(command & ~ENTRY_MODE_SET)
        elif command & RETURN_HOME:
            self.home()
        elif command & CLEAR_DISPLAY:
            self.clear()
        else:
            raise ValueError(f"Unknown command pattern: {bin(command)}")

    def clear(self):
        self.ddram_address = 0
        self.shift = 0
        self.cgram_mode = False
        if self.ddram is None:
            self.ddram = (bytearray(_DDRAM_BANK_SIZE), bytearray(_DDRAM_BANK_SIZE))
        for row in self.ddram:
            row[:] = b" " * _DDRAM_BANK_SIZE

    def home(self):
        self.ddram_address = 0
        self.shift = 0
        self.cgram_mode = False

    def entry_mode_set(self, entry_mode):
        self.entry_mode = entry_mode

    def display_control(self, display_state):
        self.display_state = display_state

    def cursor_shift(self, cursor_shift):
        move_right = cursor_shift & MOVE_RIGHT
        delta = -1 if move_right else 1
        if cursor_shift & DISPLAY_MOVE:
            if self.shift is None:
                raise RuntimeError("Unsure of current shift.")
            self.shift = (self.shift - delta) % _DDRAM_BANK_SIZE
        else:
            if self.ddram_address is None:
                raise RuntimeError("Unsure of current cursor position.")
            self.increment_ddram_address(delta)
            self.cgram_mode = False

    def function_set(self, function_settings):
        self.function_settings = function_settings

    def set_cgram_addr(self, address):
        self.cgram_address = address
        self.cgram_mode = True

    def set_ddram_addr(self, address):
        self.ddram_address = address
        self.cgram_mode = False

    def increment_ddram_address(self, delta: int = 1):
        column, row = self.cursor
        row = row + (column + delta) // _DDRAM_BANK_SIZE
        column = (column + delta) % _DDRAM_BANK_SIZE
        self.ddram_address = (row << 6) | column

    @property
    def cursor(self):
        if self.ddram_address is None:
            raise RuntimeError("Unsure of current cursor position.")
        return (self.ddram_address & 0b111111, self.ddram_address >> 6)

    @property
    def visible_columns(self):
        if self.shift is None:
            raise RuntimeError("Unsure of current shift.")
        return (self.shift, (self.shift + self.size[0]) % _DDRAM_BANK_SIZE)

    @property
    def display_on(self) -> bool:
        if self.display_state is None:
            raise RuntimeError("Unsure of current display state.")
        else:
            return bool(self.display_state & DISPLAY_ON)

    @property
    def cursor_on(self) -> bool:
        if self.display_state is None:
            raise RuntimeError("Unsure of current display state.")
        else:
            return bool(self.display_state & CURSOR_ON)

    @property
    def blink_on(self) -> bool:
        if self.display_state is None:
            raise RuntimeError("Unsure of current display state.")
        else:
            return bool(self.display_state & BLINK_ON)


class HD44780:
    """HD44780-style displays"""

    _state: HD44780_State | None = None

    def __init__(self, size: tuple[int, int] = (16, 2), font: int = FONT_5x8_DOTS, track: bool = True):
        self._size = size
        self._font = font
        self._track = track
        if track:
            self._state = HD44780_State(size)

    def command(self, command: int, arguments: int = 0):
        data = command | arguments
        self._writeto_mem(0x80, data)

    def write(self, data: int):
        self._writeto_mem(0x40, data)

    def clear(self):
        self.command(CLEAR_DISPLAY)

    def home(self):
        self.command(RETURN_HOME)

    def entry_mode(self, cursor: int = CURSOR_LEFT, shift: int = SHIFT_DECREMENT):
        entry_mode = cursor | shift
        if self._state and entry_mode == self._state.entry_mode:
            # nothing to do
            return
        self.command(ENTRY_MODE_SET, entry_mode)

    def display_control(self, display: int = DISPLAY_OFF, cursor: int = CURSOR_OFF, blink: int = BLINK_OFF):
        display_state = display | cursor | blink
        if self._state and display_state == self._state.display_state:
            # nothing to do
            return
        self.command(DISPLAY_CONTROL, display_state)

    def cursor_shift(self, cursor_shift: int = CURSOR_MOVE, direction: int = MOVE_RIGHT):
        cursor_shift_state = cursor_shift | direction
        self.command(CURSOR_SHIFT, cursor_shift_state)

    def function_set(self):
        function_settings = self._font
        if self._size[1] > 1:
            function_settings |= LINES_2
        self.command(FUNCTION_SET, function_settings)

    def set_cgram_address(self, address: int):
        if self._state and address == self._state.cgram_address:
            # nothing to do
            return
        self.command(SET_CGRAM_ADDR, address)

    def set_ddram_address(self, address: int):
        if self._state and address == self._state.ddram_address:
            # nothing to do
            return
        self.command(SET_DDRAM_ADDR, address)

    def write_ddram(self, cursor: tuple[int, int], data: bytes):
        self.cursor = cursor
        for c in data:
            self.write(c)

    def write_character(self, index: int, data: list[int]):
        self.set_cgram_address(index * 8)
        for line in data:
            self.write(line)

    def clear_cgram(self):
        self.set_cgram_address(0)
        for _ in range(_CGRAM_BANK_SIZE):
            self.write(0x00)

    def _writeto_mem(self, control: int, data: int):
        """Subclasses override this."""
        if self._state is not None:
            self._state._writeto_mem(control, data)

    @property
    def cursor(self) -> tuple[int, int]:
        if not self._state:
            raise RuntimeError("Unsure of current cursor position.")
        return self._state.cursor

    @cursor.setter
    def cursor(self, value):
        address = value[1] * 0x40 + value[0]
        self.set_ddram_address(address)

    @property
    def display_on(self) -> bool:
        if not self._state:
            raise RuntimeError("Unsure of current display state.")
        return self._state.display_on

    @display_on.setter
    def display_on(self, value: bool):
        if not self._state:
            raise RuntimeError("Unsure of current display state.")
        self.display_control(
            DISPLAY_ON if value else DISPLAY_OFF,
            CURSOR_ON if self._state.cursor_on else CURSOR_OFF,
            BLINK_ON if self._state.blink_on else BLINK_OFF,
        )

    @property
    def cursor_on(self) -> bool:
        if not self._state:
            raise RuntimeError("Unsure of current display state.")
        return self._state.cursor_on

    @cursor_on.setter
    def cursor_on(self, value: bool):
        if not self._state:
            raise RuntimeError("Unsure of current display state.")
        self.display_control(
            DISPLAY_ON if self._state.display_on else DISPLAY_OFF,
            CURSOR_ON if value else CURSOR_OFF,
            BLINK_ON if self._state.blink_on else BLINK_OFF,
        )

    @property
    def blink_on(self) -> bool:
        if not self._state:
            raise RuntimeError("Unsure of current display state.")
        return self._state.cursor_on

    @blink_on.setter
    def blink_on(self, value: bool):
        if not self._state:
            raise RuntimeError("Unsure of current display state.")
        self.display_control(
            DISPLAY_ON if self._state.display_on else DISPLAY_OFF,
            CURSOR_ON if self._state.cursor_on else CURSOR_OFF,
            BLINK_ON if value else BLINK_OFF,
        )
