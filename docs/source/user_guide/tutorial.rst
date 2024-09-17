========
Tutorial
========

When writing an application you often want to do multiple things at once.
In standard Python there are a number of ways of doing this: multiprocessing,
multithreading, and asyncio (plus other, more specialized systems, such as
MPI).  In micropython there are fewer choices: multiprocessing and
multithreading are either not available or are limited, so asyncio is
commonly used, particularly when precise timing is not an issue.

Asyncio Basics
--------------

The primary interface of the :py:mod:`asyncio` module for both Python and
Micropython is an loop that schedules :py:class:`~asyncio.Task` instances
to run.  The :py:class:`~asyncio.Task` instances can in turn choose to
pause their execution and pass control back to the event loop to allow
another :py:class:`~asyncio.Task` to be scheduled to run.

In this way a number of :py:class:`~asyncio.Task` instances can *cooperate*,
each being run in turn.  This is well-suited to code which spends most of its
time waiting for something to happen ("I/O bound"), rather than heavy
computational code ("CPU bound").

Tasks
~~~~~

To create a task you need to create an ``async`` function, which should at
one or more points ``await`` another async function.  For example, a task
which waits for a second and then prints something would be created as
follows::

    import asyncio

    async def slow_hello():
        await asyncio.sleep(1.0)
        print("Hello world, slowly.")

    slow_task = asyncio.create_task(slow_hello())

while a task that waits for only 10 milliseconds, befoer printing would
be created with::

    async def quick_hello():
        await asyncio.sleep(0.01)
        print("Hello world, quickly.")

    quick_task = asyncio.create_task(quick_hello())

At this point the tasks have been created, but they need to be run.  This
is done by running :py:func:`asynicio.gather` with the tasks::

    asyncio.run(asyncio.gather(slow_task, quick_task))

which starts the event loop and waits for the tasks to complete (potentially
running forever if they don't ever return).

Async iterators
~~~~~~~~~~~~~~~

Python and Micropython also have the notion of asynchronous iterables and
iterators: these are objects which can be used in a special ``async for``
loop where they can pause between iterations of the loop.  Internally
this is done by implementing the :py:meth:`__aiter__` and
:py:meth:`__anext__` "magic methods"::

    class SlowIterator:

        def __init__(self, n):
            self.n = n
            self.i = 0

        def __aiter__(self):
            return self

        async def __anext__(self):
            i = self.i
            if i >= n:
                raise StopAsyncIteration()
            else:
                await asyncio.sleep(1.0)
                self.i += 1
                return i

which can the be used as follows in an ``async`` function::

    async def use_iterator():
        async for i in SlowIterator(10):
            print(i)

which can in turn be used to create a :py:class:`~asyncio.Task`.

Python has a very nice way to create asynchronous iterators using asynchronous
generator functions.  The following is approximately equivalent to the previous
example::

    async def slow_iterator(n):
        for i in range(n):
            async yield i

However Micropython doesn't support asynchronous generators as of this writing.
This lack is a primary motivation for a Ultimo as a library.

Hardware and Asyncio
--------------------

Asynchronous code can greatly simplify hardware access on microcontrollers.
For example, the Raspberry Pi Pico has an on-board temperature sensor that
can be accessed via the analog-digital converter.  Many tutorials
show you how to read from it using code that looks something like the
following::

    from machine import ADC
    import time

    def temperature():
        adc = ADC(ADC.CORE_TEMP)
        while True:
            # poll the temperature every 10 seconds
            time.sleep(10.0)
            value = adc.read_u16()
            t = 27 - (3.3 * value / 0xFFFF - 0.706) / 0.001721
            print(t)

    if __name__ == '__main__':
        temperature()

but because this is synchronous code the microcontroller can't do anything
else while it is sleeping.  For example, let's say we also wanted to print
the current time from the real-time clock.  We'd need to interleave these
inside the for loop::

    from machine import ADC, RTC
    import time

    def temperature_and_time():
        adc = ADC(ADC.CORE_TEMP)
        rtc = RTC()
        temperature_counter = 0
        old_time = None
        while True:
            # poll the time every 0.1 seconds while waiting for time to change
            time.sleep(0.1)
            current_time = rtc.datetime()
            # only print when time changes
            if current_time != old_time:
                print(current_time)
                old_time = current_time

                # check to see if want to print temperature as well
                temperature_counter += 1
                if temperature_counter == 10:
                    value = adc.read_u16()
                    t = 27 - (3.3 * value / 0xFFFF - 0.706) / 0.001721
                    print(t)
                    temperature_counter = 0

    if __name__ == '__main__':
        temperature_and_time()

This is not very pretty, and gets even more difficult to handle if you have
more things going on.

We can solve this using asynchronous code::

    from machine import ADC, RTC
    import asyncio

    async def temperature():
        adc = ADC(ADC.CORE_TEMP)
        while True:
            # poll the temperature every second
            asyncio.sleep(10.0)
            value = adc.read_u16()
            t = 27 - (3.3 * value / 0xFFFF - 0.706) / 0.001721
            print(t)

    async def clock():
        rtc = RTC()
        old_time = None
        while True:
            # poll the clock every 100 milliseconds
            asyncio.sleep(0.1)
            current_time = rtc.datetime()
            # only print when time changes
            if current_time != old_time:
                print(current_time)
                old_time = current_time

    async def main():
        temperature_task = asyncio.create_task(temperature())
        clock_task = asyncio.create_task(clock())
        await asyncio.gather(temperature_task, clock_task)

    if __name__ == '__main__':
        asyncio.run(main())

This is very nice, but if you put on your software architect hat, you will
notice a lot of similarity between these methods: essentially they are looping
forever while the generate a flow of values which are then processed.

Hardware Sources
----------------

Asynchronous iterators provide a very nice way of processing a data flow
coming from hardware.  The primary thing which the Ultimo library provides
is a collection of asynchronous iterators that interact with standard
microcontroller hardware.  In particular, Ultimo has classes for polling
analog-digital converters and the real-time clock. Using these we get::

    import asyncio

    from ultimo_machine.gpio import PollADC
    from ultimo_machine.time import PollRTC

    async def temperature():
        for value in PollADC(ADC.CORE_TEMP, 10.0):
            t = 27 - (3.3 * value / 0xFFFF - 0.706) / 0.001721
            print(t)

    async def clock():
        old_time = None
        for current_time in PollRTC(0.1):
            current_time = rtc.datetime()
            if current_time != old_time:
                print(current_time)
                current_time = old_time

    async def main():
        temperature_task = asyncio.create_task(temperature())
        clock_task = asyncio.create_task(clock())
        await asyncio.gather(temperature_task, clock_task)

    if __name__ == '__main__':
        asyncio.run(main())

Ultimo calls these asynchronous iterators _sources_ and they all subclass
from the :py:class:`~ultimo.core.ASource` abstract base class.  There are
additional sources which come from polling pins, from pin or timer interrupts,
and from streams such as standard input, files and sockets.

For hardware which is not currently wrapped, Ultimo provides a
:py:class:`~ultimo.poll.poll` decorator that can be used to wrap a standard
micropython function and poll it at a set frequency.  For example::

    from ultimo.poll import poll

    @poll
    def noise():
        return random.uniform(0.0, 1.0)

    async def print_noise():
        # print a random value every second
        for value in noise(1.0):
            print(value)

Pipelines
---------

If you look at the :py:func:`clock` function in the previous example, you
will see that some of its complexity comes from the desire to print the
clock value only when the value changes: we want to *de-duplicate* consecutive
values.

Similarly, when running the code you may notice that the temperature values are
somewhat noisy, and it would be nice to be able to *smooth* the readings over
time.

In addition to the hardware sources, Ultimo has a mechanism to build processing
pipelines with streams.  Ultimo calls these _pipelines_ and provides a
collection of commonly useful operations.

In particular, there is the :py:class:`~ultimo.pipelines.Dedup` pipeline which
handles removing consecutive duplicates, so we can re-write the
:py:func:`clock` function as::

    from ultimo.pipelines import Dedup
    from ultimo_machine.time import PollRTC

    async def clock():
        for current_time in Dedup(PollRTC(0.1)):
            print(current_time)

There is also the :py:class:`~ultimo.pipelines.EWMA` pipeline which smooths
values using an exponentially-weighted moving average (which has the
advantage of being efficient to compute).  With this we can re-write the
:py:func:`temperature` function as::

    async def temperature():
        for value in EWMA(0.2, PollADC(ADC.CORE_TEMP, 10.0)):
            t = 27 - (3.3 * value / 0xFFFF - 0.706) / 0.001721
            print(t)

Ultimo provides additional pipelines for filtering, debouncing, and simply
applying a function to the data flow.

Pipeline Decorators
~~~~~~~~~~~~~~~~~~~

For the cases of applying a function or filtering a flow, Ultimo provides
function decorators to make creating a custom pipeline easy.

The computation of the temperature from the raw ADC values could be turned
into a custom filter using the :py:func:`~ultimo.pipelines.pipe` decorator::

    from ultimo.pipeline import pipe

    @pipe
    def to_celcius(value):
        return 27 - (3.3 * value / 0xFFFF - 0.706) / 0.001721

    async def temperature():
        for value in to_celcius(EWMA(0.2, PollADC(ADC.CORE_TEMP, 10.0))):
            t = 27 - (3.3 * value / 0xFFFF - 0.706) / 0.001721
            print(t)

There is an analagous :py:func:`~ultimo.pipelines.apipe` decorator for async
functions.  There are similar decorators :py:func:`~ultimo.pipelines.filter`
and :py:func:`~ultimo.pipelines.afilter` that turn a function that produces
boolean values into a filter which supresses values which return ``False``.

Pipe Notation
~~~~~~~~~~~~~

The standard functional notation for building pipelines can be confusing
when there are many terms involved.  Ultimo provides an alternative notation
using the bitwise-or operator as a "pipe" symbol in a way that may be familiar
to unix command-line users.

For example, the expression::

    to_celcius(EWMA(0.2, PollADC(ADC.CORE_TEMP, 10.0)))

can be re-written as::

    PollADC(ADC.CORE_TEMP, 10.0) | EWMA(0.2) | to_celcius()

Values move from left-to-right from the source through subsequent pipelines.
This notation makes it clear which attributes belong to which parts of the
overall pipeline.

In terms of behaviour, the two notations are equivalent, so which is used is
a matter of preference.

Hardware Sinks
--------------

Getting values from hardware is only half the story.  We would also like to
control hardware from our code, whether turning an LED on, or displaying text
on a screen.

Let's continue our example by assuming that we add a potentiometer to the
setup and use it to control a LED's brightness via pulse-width modulation.

Using an Ultimo hardware source, we would add the following code to our
application::

    from machine import PWM

    # Raspberry Pi Pico pin numbers
    ADC_PIN = 26
    ONBOARD_LED_PIN = 25

    async def led_brightness():
        pwm = PWM(ONBOARD_LED_PIN, freq=1000, duty_u16=0)
        for value in PollADC(ADC_PIN, 0.1):
            pwm.duty_u16(value)

    async def main():
        temperature_task = asyncio.create_task(temperature())
        clock_task = asyncio.create_task(clock())
        led_brightness_task = asyncio.create_task(led_brightness())
        await asyncio.gather(temperature_task, clock_task, led_brightness)

..  note::

    The above doesn't work on the Pico W as the onboard LED isn't accessible
    to the PWM hardware.  Use a different pin wired to an LED and resistor
    between 50 and 330 ohms.

Again, if we put on our software architect's hat we will realize that all tasks
which set the pluse-width modulation duty cycle of pin will look very much the same::

    async def set_pwm(...):
        pwm = PWM(...)
        for value in ...:
            pwm.duty_u16(value)

Ultimo provides a class which encapsulates this pattern:
:py:class:`~ultimo_machine.gpio.PWMSink`.  So rather than writing a dedicated async
function, the :py:class:`~ultimo_machine.gpio.PWMSink` class can simply be appended
to the pipeline. Additionally it has a convenience method
:py:class:`~ultimo.core.ASink.create_task`::

    async def main():
        temperature_task = asyncio.create_task(temperature())
        clock_task = asyncio.create_task(clock())

        led_brightness = PollADC(ADC_PIN, 0.1) | PWMSink(ONBOARD_LED_PIN, 1000)
        led_brightness_task = led_brightness.create_task()

        await asyncio.gather(temperature_task, clock_task, led_brightness_task)

This sort of standardized pipeline-end is called a *sink* by Ultimo, and all
sinks subclass the :py:class:`~ultimo.core.ASink` abstract base class.  In
addition to :py:class:`~ultimo_machine.gpio.PWMSink` there are standard sinks
for output to GPIO pins, writeable streams (such as files, sockets and
standard output), and text displays.

Where Ultimo doesn't yet provide a sink, the :py:func:`~ultimo.core.sink`
decorator allows you to wrap a standard Micropython function which takes an
input value and consumes it.  For example, we could print nicely formatted
Celcius temperatures using::

    @sink
    def print_celcius(value):
        print(f"{value:2.1f}°C")

    async def main():
        temperature = PollADC(ADC.CORE_TEMP, 10.0) | EWMA(0.2) | to_celcius() | print_celcius()
        temperature_task = temperature.create_task()
        ...

Application State
-----------------

While you can get a lot done with data flows from sources to sinks, almost all
real applications need to hold some state, whether something as simple as the
location of a cursor up to the full engineering logic of a complex app.  You
may want hardware to do things depending on updates to that state.  Often it
may be enough to just use the current values of state stored as Micropython
objects when updating for other reasons.  But sometimes you want to react to
changes in the current state.

Ultimo has a :py:class:`~ultimo.values.Value` source which holds a Python
object and emits a flow of values as that held object changes.

For example, an application which is producing audio might hold the output
volume in a :py:class:`~ultimo.values.Value` and then have one or more
streams which flow from it: perhaps one to set values on the sound system,
another to display a volume bar in on a screen, or another to set the
brightness of an LED::

    @pipe
    def text_bar(volume):
        bar = ("=" * (volume >> 12))
        return f"Vol: {bar:<16s}"

    async def main():
        # volume is an unsigned 16-bit int
        volume = Value(0)
        led_brightness = volume | PWMSink(ONBOARD_LED_PIN, 1000)

        text_device = ...
        volume_bar = volume | text_bar() | text_device.display_text(0, 0)
        ...

It's also common for a :py:class:`~ultimo.values.Value` to be set at the end
of a pipeline, and for this the value provides a dedicated
:py:attr:`~ultimo.values.Value.sink`, but also can be used at the end of a
pipeline.  For example, to control the volume with a potentiometer, you could
have code which looks like::

    async def main():
        # volume is an unsigned 16-bit int
        volume = Value(0)
        set_volume = ADCPoll(ADC_PIN, 0.1) | volume
        led_brightness = volume | PWMSink(ONBOARD_LED_PIN, 1000)

In addition to the simple :py:class:`~ultimo.values.Value` class, there are
additional value subclasses which smooth value changes using easing functions
and another which holds a value for a set period of time before resetting to
a default.

Conclusion
----------

As you can see Ultimo provides you with the building-blocks for creating
interfaces which allow you to build applications which smoothly work together.
Since it is built on top of the standard Micropython :py:mod:`asyncio` it
interoperates with other async code that you might write.  If you need to it
is generally straightforward to write your own sources, sinks and pipelines
with a little understanding of Python and Micropython's asyncio libraries.
