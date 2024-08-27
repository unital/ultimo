Ultimo
======

An experimental interface framework for micropython built around
asynchronous iterators.

Core Concepts
-------------

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
        brightness_task = asyncio.Task(control_brightness(led, adc))
        display_task = asyncio.Task(display_time(lcd, clock))
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

Iterator API
------------

Ultimo provides a slightly richer API for its iterator objects.  In addition
to being used in ``async for ...`` similar iterator contexts, the iterator
objects can be called to generate an immediate value (eg. by querying the
underlying hardware, or returning a cached value).

Polling
-------

The simplest way to create an interator is by polling a callable at an
interval, for example::

    from machine import RTC

    rtc = RTC()
    clock = Poll(rtc.datetime, interval=1)

or::

    from machine import ADC, Pin

    _adc = ADC(Pin(19))
    adc = Poll(_adc.read_16, interval=0.01)

The Poll object expects the callable to be called with no arguments, so more
complex signatures may need to be wrapped in a helper function, partial or
callable class, as appropriate.  The callable should be a regular synchronous
function which should ideally avoid setting any shared state (or carefully
use locks if it must).

Poll objects can also be called, which simply invokes to the underlying
callable.

The library includes factory functions for common poll-based data sources.

Interrupts
----------

The other common way of getting data is via interrupts.  While there is no
helper for creating interrupt-based iterators, the basic idea is to create
an ``asyncio.ThreadSafeFlag``, set that in the interrupt handler, and then
have the iterator ``await`` the flag, perform any processing, and then reset
the flag.

As with all interrupt-based code in micropython, care needs to be taken in
the interrupt handler and the iterator method so that the code is fast,
robust and reentrant.

Pipelines
---------

Often you want to do some further processing on the raw output from a device.
For example, you may want to convert the data into a more useful format,
smooth a noisy signal, debounce a button press, or de-duplicate a repetitive
iterator.

For example, a raw ADC output could be converted to a voltage as follows::

    def voltage(raw_value):
        return 3.3 * raw_value / 0xffff

and then this used to wrap the output of an ADC iterator::

    adc_volts = Apply(adc, voltage)

More succinctly, the ``pipe`` decorator can be used as follows::

    @pipe
    def voltage(raw_value):
        return 3.3 * raw_value / 0xffff

    adc_volts = voltage(adc)

Consumers
---------

A common pattern for the eventual result of a chain of iterators is a simple
async for loop which looks something like::

    # get an immediate initial value
    consume(producer())

    # consume forever
    async for value in producer:
        consume(value)

This is common enough that Ultimo provides ``connect`` function and
``consumer`` decorator to reduce the amount of boilerplate code::

    connect(adc_256, led.brightness)

Putting It All Together
-----------------------

Let's consider a system where we have:

- an lcd with an led backlight which use I2C
- a push button on GPIO pin 0
- a potentiometer on pin 19

and we want the behaviour:

- the push button turns the led and lcd on and off
- the potentiometer controls the brightness of the led
- the lcd displays the current time in minutes

The potentiometer needs its raw value converted to a range 0-255 for the led,
and we only want to change the value when the value actually changes, so we
use::

    @pipe
    def brightness(raw_value):
        return raw_value >> 8

    brightness_task = Task(connect(led.brightness, dedup(brightness(adc(19)))))

The time for the lcd needs formatting and deduplication::

    @pipe
    def hours_minutes(dt):
        return dt[4:6]

    @pipe
    def format(t):
        return b'{0:02}:{1:02}'.format(*t)

    @consume
    def display_bytes(value):
        lcd.clear()
        lcd.write_ddram(value)

    time_task = Task(display_bytes(format(dedup(hours_minutes(poll_rtc(1.0))))

The button is a simple GPIO, but is noisy and needs de-bouncing, so we use
an interrupt::

    async def on_off(button):
        state = False
        async for _ in button:
            state = not state
            if state:
                brightness_task = Task(connect(led.brightness, dedup(brightness(adc(19)))))
                time_task = Task(display_bytes(format(dedup(hours_minutes(poll_rtc(1.0))))
            else:
                brightness_task.cancel()
                time_task.cancel()

    async def main():
        button = debounce(button(pin))
        task = Task(on_off(button))
        await gather(task)

    if __name__ == '__main__':
        run(main())
