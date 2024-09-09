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

What Ultimo Isn't
-----------------

Ultimo isn't intended for strongly constrained real-time applications, since
:py:mod:`asyncio` is cooperative multitasking and gives no guarantees about
the frequency or latency with which a coroutine will be called.

The design goal of Ultimo was to make it easier to support user interactions,
so it may not be a good fit for applications which are purely for hardware
automation.
