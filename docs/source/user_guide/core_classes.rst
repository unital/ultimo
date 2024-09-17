============
Core Classes
============

.. currentmodule:: ultimo

The core classes are the building-blocks for Ultimo.  They defined the basic
behaviour of the asynchronous iterators that define the application data flow.

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

As with all interrupt-based code in Micropython, care needs to be taken in
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