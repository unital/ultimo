===============
Machine Classes
===============

.. currentmodule:: ultimo_machine

The classes definied in :py:mod:`ultimo_machine` handle interaction with
standard hardware interfaces provided by microcontrollers: GPIO pins, ADC,
PWM, timers, etc.  These are generally sources or sinks.

GPIO
====

.. currentmodule:: ultimo_machine.gpio

The :py:mod:`ultimo_machine.gpio` module contains sources and sinks based
on GPIO pins and related functionality.  The module provides the following
sources:

.. autosummary::

    PollPin
    PollSignal
    PollADC
    PinInterrupt

and the following sinks:

.. autosummary::

    PinSink
    SignalSink
    PWMSink

All of these expect a pin ID to know which pin they should use. The "Pin" and
"Signal" classes need to know whether the pin is pulled up or down and emit or
expect boolean values.

The :py:class:`PollADC` produces unsigned 16-bit integer values (ie. 0-65535)
and :py:class:`PWMSink` expects to consume values in that range which are used
to set the duty cycle.  The :py:class:`PWMSink` also needs to know the frequency
with which to drive the pulses, and can be given an optional initial duty cycle.

The :py:class:`PinInterrupt` class needs to know whether the pin is pulled up
or down and what pin events should trigger it (it defaults to
:py:const:`machine.Pin.IRQ_RISING`).  When triggered it emits the value of the
pin at the time when the asyncio callback is run, which may or may not match
the value of the pin at the time that the interrupt happened.  The class also
provides an async context manager that handles setting and removing the
interrupt handler on the pin.  Typical usage looks something like::

    async with PinInterrupt(PIN_ID, Pin.PULL_UP, Pin.IRQ_FALLING) as interrupt:
        # do something with the interrupt
        ...

Time
====

.. currentmodule:: ultimo_machine.time

The :py:mod:`ultimo_machine.gpio` module provides the following time-related
sources:

.. autosummary::

    PollRTC
    TimerInterrupt

The :py:class:`PollRTC` class can be passed the ID of the RTC to use along with
an initial datetime tuple (if supported by the hardware) and the polling
interval.  The values emitted are datetime tuples as returned by the
:py:meth:`machine.RTC.datetime` method.

The :py:class:`TimerInterrupt` class must be passed a Timer ID, along with the
timing mode (which defaults to :py:const:`machine.Timer.PERIODIC`) and either
the frequency or period.  The timer's iterator emits a :py:const:`True` value
whenever it is triggered.  It also can be used as a context manager to set and
remove the interrupt handler.  Typical usage looks something like::

    async with TimerInterrupt(TIMER_ID, freq=10) as interrupt:
        # do something with the interrupt
        ...

..  note::

    Because the timer is calling back via asyncio, any behaviour depending on
    the interrupt will incur latency from the asyncio scheduling, and so it's
    clear that this class provides much, if any, advantage over delaying using
    :py:func:`uasyncio.sleep`, particularly for one-shot timers.
