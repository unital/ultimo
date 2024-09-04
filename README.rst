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

ASource Classes
---------------

Ultimo provides a slightly richer API for its iteratable objects.  In addition
to being used in ``async for ...`` similar iterator contexts, the iteratable
objects can be asynchronously called to generate an immediate value (eg. by
querying the underlying hardware, or returning a cached value).  This protocol
is embodied in the :py:class:`ASource` base class.

The corresponding iterator objects are subclasses of :py:class:`AFlow` and
by default each :py:class:`ASource` has a particular :py:class:`AFlow` subclass
that it creates when iterating.

Ultimo has a number of builtin :py:class:`ASource` subclasses that handle common
cases.

Poll
~~~~

The simplest way to create a source is by polling a callable at an interval.
The :py:class:`Poll` class does this.  For example::

    from machine import RTC

    rtc = RTC()
    clock = Poll(rtc.datetime, interval=1)

or::

    from machine import ADC, Pin

    _adc = ADC(Pin(19))
    adc = Poll(_adc.read_16, interval=0.01)

The Poll object expects the callable to be called with no arguments, so more
complex function signatures may need to be wrapped in a helper function,
partial or callable class, as appropriate.  The callable can be a regular
synchronous function or asyncrhonous coroutine, which should ideally avoid
setting any shared state (or carefully use locks if it must).

Poll objects can also be called, which simply invokes to the underlying
callable.

EventSource
~~~~~~~~~~~

The alternative to polling is to wait for an asynchronous event.  The
:py:class:`EventSource` asbtract class provides the basic infrastructure for
users to subclass by providing an appropriate :py:meth:`__call__` method.

The event that the iterator waits for can be either an :py:class:`asyncio.Event`
set by regular Python code calling the :py:meth:`fire` method, or an
:py:class:`asyncio.ThreadSafeFlag` which can (carefully!) be set in an interrupt
handler.

For example, the following class provides a class for handling IRQs from a Pin::

    class Interrupt(EventSource):

        def __init__(self, pin, trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING):
            self.event = asyncio.ThreadSafeFlag()
            self.pin = pin
            self.trigger = trigger

        async def __aenter__(self):
            set_flag = self.event.set

            def isr(_):
                set_flag()

            self.pin.irq(isr, self.trigger)

            return self

        async def __aexit__(self, *args, **kwargs):
            await self.close()
            return False

        async def __call__(self):
            return self.pin()

        async def close(self):
            self.pin.irq()

As with all interrupt-based code in micropython, care needs to be taken in
the interrupt handler and the iterator method so that the code is fast,
robust and reentrant.

Values and Easings
~~~~~~~~~~~~~~~~~~

A :py:class:`Value` is an :py:class`EventSource` which holds a value as state
and fires an event every time the value is updated (either by calling the
instance with the new value, or calling the :py:meth:`update` method).
Iterating over a :py:class:`Value` asynchronously generates the values as they
are changed.

An :py:class:`Easing` is a value which when set is transitioned into its new
value over time by an easing formula.  The intermediate values will be emitted
by the iterator.

Pipelines
---------

Often you want to do some further processing on the raw output from a device.
For example, you may want to convert the data into a more useful format,
smooth a noisy signal, debounce a button press, or de-duplicate a repetitive
iterator.  Ultimo provides the :py:class:`APipeline` base class for sources
which transform another source.

These include:

- :py:class:`Apply` - apply a function to each value
- :py:class:`Filter` - filter values using a function, discarding ``False`` values
- :py:class:`EWMA` - smooth values using an exponentially-weighted moving average
- :py:class:`Dedup` - discard sequential duplicated values
- :py:class:`Debounce` - let a source settle before resuming outputs
-


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
                brightness_task = create_task(connect(led.brightness, dedup(brightness(adc(19)))))
                time_task = create_task(display_bytes(format(dedup(hours_minutes(poll_rtc(1.0))))
            else:
                brightness_task.cancel()
                time_task.cancel()

    async def main():
        button = debounce(button(pin))
        task = Task(on_off(button))
        await gather(task)

    if __name__ == '__main__':
        run(main())

What Ultimo Isn't
-----------------

Ultimo isn't intended for strongly constrained real-time applications, since
:py:mod:`asyncio` is cooperative multitasking and gives no guarantees about
how frequently a coroutine will be called.

The design goal of Ultimo was to make it easier to support user interactions,
so it may not be a good fit for applications which are purely for hardware
automation.
