# SPDX-FileCopyrightText: 2024-present Unital Software <info@unital.dev>
#
# SPDX-License-Identifier: MIT

from machine import ADC, PWM, Pin, Signal

from ultimo.core import ASink, ThreadSafeSource, asynchronize
from ultimo.poll import Poll


class PollPin(Poll):
    """A source which sets up a pin and polls its value."""

    def __init__(self, pin_id, pull, interval=0.001):
        self.pin = Pin(pin_id)
        self.pull = pull
        super().__init__(asynchronize(self.pin.value), interval)
        self.init()

    def init(self):
        self.pin.init(Pin.IN, self.pull)


class PollSignal(Poll):
    """A source which sets up a Singal on a pin and polls its value."""

    def __init__(self, pin_id, pull, invert=False, interval=0.001):
        self.signal = Signal(pin_id, Pin.IN, pull, invert=invert)
        super().__init__(asynchronize(self.signal.value), interval)


class PollADC(Poll):
    """A source which sets up an ADC and polls its value."""

    def __init__(self, pin_id, interval=0.001):
        self.adc = ADC(pin_id)
        super().__init__(asynchronize(self.adc.read_u16), interval)


class PinInterrupt(ThreadSafeSource):
    """A source triggered by an IRQ on a pin.

    The class acts as a context manager to set-up and remove the IRQ handler.
    """

    def __init__(self, pin_id, pull, trigger=Pin.IRQ_RISING):
        super().__init__()
        self.pin = Pin(pin_id)
        self.pull = pull
        self.trigger = trigger

    async def __aenter__(self):
        set_flag = self.event.set

        def isr(_):
            set_flag()

        self.pin.init(Pin.IN, self.pull)
        self.pin.irq(isr, self.trigger)

        return self

    async def __aexit__(self, *args, **kwargs):
        await self.close()
        return False

    async def __call__(self):
        return bool(self.pin())

    async def close(self):
        self.pin.irq()


class PinSink(ASink):
    """A sink that sets the value on a pin."""

    def __init__(self, pin_id, pull, source=None):
        super().__init__(source)
        self.pin = Pin(pin_id)
        self.pull = pull
        self.init()

    def init(self):
        self.pin.init(Pin.OUT, self.pull)

    async def process(self, value):
        self.pin.value(value)


class SignalSink(ASink):
    """A sink that sets the value of a signal."""

    def __init__(self, pin_id, pull, invert=False, source=None):
        super().__init__(source)
        self.signal = Signal(pin_id, Pin.OUT, pull, invert=invert)

    async def process(self, value):
        self.signal.value(value)


class PWMSink(ASink):
    """A sink that sets pulse-width modulation on a pin."""

    def __init__(self, pin_id, frequency, duty_u16=0, source=None):
        super().__init__(source)
        self.pwm = PWM(Pin(pin_id, Pin.OUT), freq=frequency, duty_u16=duty_u16)

    async def process(self, value):
        self.pwm.duty_u16(value)
