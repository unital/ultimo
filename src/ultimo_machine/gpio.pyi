# SPDX-FileCopyrightText: 2024-present Unital Software <info@unital.dev>
#
# SPDX-License-Identifier: MIT

from typing import Self

from machine import ADC, PWM, Pin, Signal

from ultimo.core import ASource, ASink, ThreadSafeSource, asynchronize
from ultimo.poll import Poll


class PollPin(Poll[bool]):
    """A source which sets up a pin and polls its value."""

    def __init__(self, pin_id: int, pull: int, interval: float = 0.001): ...

    def init(self) -> None: ...


class PollSignal(Poll[bool]):
    """A source which sets up a Singal on a pin and polls its value."""

    def __init__(self, pin_id: int, pull: int, invert: bool = False, interval=0.001): ...


class PollADC(Poll[int]):
    """A source which sets up an ADC and polls its value."""

    def __init__(self, pin_id: int, interval=0.001): ...


class PinInterrupt(ThreadSafeSource[bool]):
    """A source triggered by an IRQ on a pin.

    The class acts as a context manager to set-up and remove the IRQ handler.
    """

    def __init__(self, pin_id: int, pull: int, trigger: int = Pin.IRQ_RISING): ...

    async def __aenter__(self) -> Self: ...

    async def __aexit__(self, *args, **kwargs) -> bool: ...

    async def __call__(self) -> bool: ...

    async def close(self) -> None: ...


class PinSink(ASink[bool]):
    """A sink that sets the value on a pin."""

    def __init__(self, pin_id: int, pull: int, source: ASource[bool] | None = None): ...

    def init(self) -> None: ...

    async def process(self, value: bool) -> None: ...


class SignalSink(ASink[bool]):
    """A sink that sets the value of a signal."""

    def __init__(self, pin_id: int, pull: int, invert: bool = False, source: ASource[bool] | None = None): ...

    async def process(self, value: bool) -> None: ...


class PWMSink(ASink[int]):
    """A sink that sets pulse-width modulation on a pin."""

    def __init__(self, pin_id: int, frequency: int, duty_u16: int = 0, source=None): ...

    async def process(self, value: int) -> None: ...
