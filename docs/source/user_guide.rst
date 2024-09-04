=================
Ultimo User Guide
=================

.. currentmodule:: ultimo

Ultimo is an experimental interface framework for micropython built around
asynchronous iterators.

Core Concepts
=============

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

ASource Classes
===============

Ultimo provides a slightly richer API for its iteratable objects.  In addition
to being used in ``async for ...`` similar iterator contexts, the iteratable
objects can be asynchronously called to generate an immediate value (eg. by
querying the underlying hardware, or returning a cached value).  This protocol
is embodied in the |ASource| base class.

The corresponding iterator objects are subclasses of |AFlow| and
by default each |ASource| has a particular |AFlow| subclass
that it creates when iterating.

Ultimo has a number of builtin |ASource| subclasses that handle common
cases.

Poll
----

The simplest way to create a source is by polling a callable at an interval.
The |Poll| class does this.  For example::

    from machine import RTC

    rtc = RTC()
    clock = Poll(rtc.datetime, interval=1)

or::

    from machine import ADC, Pin

    _adc = ADC(Pin(19))
    adc = Poll(_adc.read_16, interval=0.01)

The |Poll| object expects the callable to be called with no arguments, so more
complex function signatures may need to be wrapped in a helper function,
partial or callable class, as appropriate.  The callable can be a regular
synchronous function or asynchronous coroutine, which should ideally avoid
setting any shared state (or carefully use locks if it must).

|Poll| objects can also be called, which simply invokes to the underlying
callable.

EventSource
-----------

The alternative to polling is to wait for an asynchronous event.  The
|EventSource| asbtract class provides the basic infrastructure for
users to subclass by providing an appropriate :py:meth:`__call__` method.
The |ThreadSafeSource| class is a subclass that uses a
:py:class:`asyncio.ThreadSafeFlag`  instead of an :py:class:`asyncio.Event`.

The event that the iterator waits for the event to be set by regular Python
code calling the :py:meth:`~ultimo.core.EventSource.fire` method, or an
interrupt handler (carefully!) setting a :py:class:`asyncio.ThreadSafeFlag`.

For example, the following class provides a class for handling IRQs from a
:py:class:`~machine.Pin`::

    class Interrupt(ThreadSafeSource):

        def __init__(self, pin, trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING):
            super().__init__()
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
robust and reentrant.  Also note that although interrupt handlers may be
fast, any |EventFlow| instances watching the event will be dispatched by
the

Streams
-------

The |ARead| source wraps a readable IO stream (:py:obj:`sys.stdin` by default)
and when iterated over returns each byte (or char from a text file) from the
stream until the stream is closed.  To help with clean-up, |ARead| is also a
async context manager that will close the stream on exit.

Values
------

A |Value| is an |EventSource| which holds a value as state
and fires an event every time the value is updated (either by calling the
instance with the new value, or calling the :py:meth:`~ultimo.value.Value.update` method).
Iterating over a |Value| asynchronously generates the values as they
are changed.

An |EasedValue| is a value which when set is transitioned into its new
value over time by an easing formula.  The intermediate values will be emitted
by the iterator.

ASink Classes
=============

..  note::

    The |ASink| class is very thin, and most behaviour can be achieved by an
    async function with an async for loop.  Currently the |AWrite| class is
    the most compelling reason for this to exist.  It's possible that this
    concept may be removed in future versions.

A common pattern for the eventual result of a chain of iterators is a simple
async for loop which looks something like::

    try:
        async for value in source:
            await process(value)
    except uasyncio.CancelError:
        pass

This is common enough that Ultimo provides an |ASink| base class which wraps
a source and has a |run| method that asynchronously consumes the source,
calling its |process| method on each generated value, until the source is
exhausted or the task cancelled.

While sinks can be generated with a source provided as an argument, they also
support a pipe-style syntax with the ``|`` operator, so rather than writing::

    source = MySource()
    sink = MySink(source=source)
    uasyncio.create_task(sink.run())

they can be connected using::

    sink = MySource() | MySink()
    uasyncio.create_task(sink.run())

Consumers
---------

In many cases, a sink just needs to asyncronously call a function.  The
|Consumer| class provides a simple |ASink| which wraps an asynchronous
callable which is called with the source values as the first argument
by the |process| method::

    async def display(value, lcd):
        lcd.write_data(value)

    lcd = ...
    display_sink = Consumer(display, lcd)

There are also helper decorators |sink| and |asink| that wrap functions
and produce factories that produce consumers for the functions::

    @sink
    def display(value, lcd):
        lcd.write_data(value)

    lcd = ...
    display_sink = display(lcd)

Streams
-------

The |AWrite| source wraps a writable IO stream (:py:obj:`sys.stdout` by
default) and consumes a stream of :py:type:`bytes` objects (or
:py:type:`str` for a text stream) which it writes to the stream until the
stream is closed.  To help with clean-up, |AWrite| is also a async context
manager that will close the stream on exit.

Pipelines
=========

.. currentmodule:: ultimo.pipelines

..  note::

    The |APipeline| class exists primarily because Micropython doesn't
    currently support asynchronous generator functions.

Often you want to do some further processing on the raw output from a device.
For example, you may want to convert the data into a more useful format,
smooth a noisy signal, debounce a button press, or de-duplicate a repetitive
iterator.  Ultimo provides the |APipeline| base class for sources
which transform another source.

These include:

.. autosummary::

    Apply
    Debounce
    Dedup
    EWMA
    Filter

For example, a raw ADC output could be converted to a voltage as follows::

    async def voltage(raw_value):
        return 3.3 * raw_value / 0xffff

and then this used to wrap the output of an ADC iterator::

    adc_volts = Apply(adc, voltage)

More succinctly, the :py:func:`~ultimo.pipelines.pipe` decorator can be used
as follows::

    @pipe
    def voltage(raw_value, max_value=3.3):
        return max_value * raw_value / 0xffff

    adc_volts = voltage(adc)

There is a similar :py:func:`~ultimo.pipelines.apipe` method that accepts an
asynchronous function.

|APipeline| subclasses both |ASource| and |ASink|, so it is both an iteratable and a
has a |run| method that can be used in a task.  Just like other |ASink| subclasses,
|APipeline| classes can use the `|` operator to compose longer data flows::

    display_voltage = ADCSource(26) | voltage() | EWMA(0.2) | display(lcd)

Custom Components
=================

.. currentmodule:: ultimo

A custom source should subclass |ASource| or one of it's abstract subclasses
such as |EventSource|, and should override the :py:meth:`__call__` async method
to get the current data value (or |process| for a pipeline).  You will also
need to decide what sort of iterator is the right one for the subclass.

The default |AFlow| iterator will await the result of calling the source and
will either immeditately return the value, or raise
:py:exc:`StopAsyncIteration` if the value is :py:const:`None`.

The |EventFlow| iterator used by |EventSource| waits on the event and evaluates
the source, but also raises if the value is :py:const:`None`.

The |APipelineFlow| iterator used by |APipeline| takes values from the input
source's flow and generates an output value by applying the pipeline to the
input value.  If the generated value is :py:const:`None`, the |APipelineFlow|
will get another value from the source and repeat until the value generated
is not :py:const:`None`.

If these are not the desired behaviours, you will want to subclass one of these
base classes (likely one that corresponds to the source you are subclassing),
and set your subclass as the :py:attr:`~ultimo.core.ASource.flow` class
attribute.

Custom |AFlow| subclasses should adhere to the rule that they should never
emit a :py:const:`None` value: on encountering :py:const:`None` from their
source they should either raise :py:exc:`StopAsyncIteration` or try to get
another value from the source.

A custom sink likely just has to subclass |ASink| and override the |process|
method.  But also note, that complex behaviour may be easier to write as a
simple asynchronous method that takes a source as input and iterates over it,
doing what needs to be done.

Putting It All Together
=======================

..  warning::

    This is currently hypothetical.  API may change.

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

    @sink
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


.. |ASource| replace:: :py:class:`~ultimo.core.ASource`
.. |AFlow| replace:: :py:class:`~ultimo.core.AFlow`
.. |ASink| replace:: :py:class:`~ultimo.core.ASink`
.. |process| replace:: :py:meth:`~ultimo.core.ASink.process`
.. |run| replace:: :py:meth:`~ultimo.core.ASink.run`
.. |APipeline| replace:: :py:class:`~ultimo.core.APipeline`
.. |APipelineFlow| replace:: :py:class:`~ultimo.core.APipelineFlow`
.. |EventSource| replace:: :py:class:`~ultimo.core.EventSource`
.. |ThreadSafeSource| replace:: :py:class:`~ultimo.core.ThreadSafeSource`
.. |EventFlow| replace:: :py:class:`~ultimo.core.EventFlow`
.. |Consumer| replace:: :py:class:`~ultimo.core.Consumer`
.. |sink| replace:: :py:func:`~ultimo.core.sink`
.. |asink| replace:: :py:func:`~ultimo.core.asink`
.. |Poll| replace:: :py:class:`~ultimo.poll.Poll`
.. |ARead| replace:: :py:class:`~ultimo.stream.ARead`
.. |AWrite| replace:: :py:class:`~ultimo.stream.AWrite`
.. |Value| replace:: :py:class:`~ultimo.value.Value`
.. |EasedValue| replace:: :py:class:`~ultimo.value.EasedValue`

