============
Introduction
============

.. currentmodule:: ultimo

The basic idea of the library is to be able to implement the logic of a
micropython application around a collection of asyncio Tasks that consume
asynchronous iterators.

For example, to make a potentiometer control the duty cycle of an RGB LED
you might do something like::

    async def control_brightness(led, adc):
        async for value in adc:
            led.brightness(value >> 8)

while to output the current time to a 16x2 LCD, you might do::

    async def display_time(lcd, clock):
        async for dt in clock:
            value = b"{4:02d}:{5:02d}".format(dt)
            lcd.clear()
            lcd.write(value)

You can then combine these into a single application by creating Tasks in
a ``main`` function::

    async def main():
        led, lcd, adc, clock = initialize()
        brightness_task = asyncio.create_task(control_brightness(led, adc))
        display_task = asyncio.create_task(display_time(lcd, clock))
        # run forever
        await asyncio.gather(brightness_task, display_task)

    if __name__ == "__main__":
        asyncio.run(main())

This is compared to the usual synchronous approach of having an infinite loop
that mixes together the logic for polling of the ADC and clock.

In addition to the code being simpler, this permits updates to be generated
and handled at different rates depending on the needs of the interaction.  For
example, the clock only needs to poll the time occasionally (since it is only
displaying hours and minutes) while the potentiometer needs to be checked
frequently if it is to be responsive to user interactions.

What Ultimo Is
--------------

The :py:mod:`ultimo` library provides classes that simplify this paradigm.
There are classes which provide asynchronous iterators based around polling,
interrupts and asynchronous streams, as well as intermediate transforming
iterators that handle common tasks such as smoothing and de-duplication.
The basic Ultimo library is hardware-independent and should work on any
recent micropython version.

The :py:mod:`ultimo_machine` library provides hardware support wrapping
the micropython :py:mod:`machine` module and other standard library
modiles.  It provides sources for simple polling of and interrupts from GPIO
pins, polled ADC, polled RTC and interrupt-based timer sources.

The :py:mod:`ultimo_display` library provides a framework for text-based
display of data, including an implementation that renders to a framebuffer.

Ultimo also provides convenience decorators and a syntax for building pipelines
from basic building blocks using the bitwise-or (or "pipe" operator)::

    @pipe
    def denoise(value):
        """Denoise uint16 values to 6 significant bits."""
        return value & 0xfc00

    async def main():
        led_brightness = PollADC(26, 0.1) | denoise() | Dedup() | PWMSink(25)
        await asyncio.gather(led_brightness.create_task())

What Ultimo Isn't
-----------------

Ultimo isn't intended for strongly constrained real-time applications, since
:py:mod:`asyncio` is cooperative multitasking and gives no guarantees about
the frequency or latency with which a coroutine will be called.

The design goal of Ultimo was to make it easier to support user interactions,
so it may not be a good fit for applications which are purely for hardware
automation.

Why "Ultimo"?
-------------

Ultimo is a suburb of my hometown of Sydney which has historically been a hub
for science and technology: it is home to the University of Technology Sydney
and the Powerhouse Museum, and is where many Sydney start-ups are located.
