Ultimo
======

Ultimo is an interface framework for Micropython built around asynchronous
iterators.

- `Documentation <https://unital.github.io/ultimo/>`_
  - `User Guide <https://unital.github.io/ultimo/user_guide.html>`_
    - `Installation <https://unital.github.io/ultimo/user_guide/installation.html>`_
    - `Tutorial <https://unital.github.io/ultimo/user_guide/tutorial.html>`_
    - `Examples <https://unital.github.io/ultimo/user_guide/examples.html>`_
  - `API <https://unital.github.io/ultimo/api.html>`_

Description
-----------

Ultimo allows you to implement the logic of a Micropython application
around a collection of asyncio Tasks that consume asynchronous iterators.
This is compared to the usual synchronous approach of having a single main
loop that mixes together the logic for all the different activities that your
application carries out.

In addition to the making the code simpler, this permits updates to be
generated and handled at different rates depending on the needs of the
activity, so a user interaction, like changing the value of a potentiometer or
polling a button can happen in milliseconds, while a clock or temperature
display can be updated much less frequently.

The ``ultimo`` library provides classes that simplify this paradigm.
There are classes which provide asynchronous iterators based around polling,
interrupts and asynchronous streams, as well as intermediate transforming
iterators that handle common tasks such as smoothing and de-duplication.
The basic Ultimo library is hardware-independent and should work on any
recent Micropython version.

The ``ultimo_machine`` library provides hardware support wrapping
the Micropython ``machine`` module and other standard library
modules.  It provides sources for simple polling of and interrupts from GPIO
pins, polled ADC, polled RTC and interrupt-based timer sources.

For example, you can write code like the following to print temperature and
time asynchronously::

    import asyncio
    from machine import ADC

    from ultimo.pipelines import Dedup
    from ultimo_machine.gpio import PollADC
    from ultimo_machine.time import PollRTC

    async def temperature():
        async for value in PollADC(ADC.CORE_TEMP, 10.0):
            t = 27 - (3.3 * value / 0xFFFF - 0.706) / 0.001721
            print(t)

    async def clock():
        async for current_time in Dedup(PollRTC(0.1)):
            print(current_time)

    async def main():
        temperature_task = asyncio.create_task(temperature())
        clock_task = asyncio.create_task(clock())
        await asyncio.gather(temperature_task, clock_task)

    if __name__ == '__main__':
        asyncio.run(main())

Ultimo also provides convenience decorators and a syntax for building pipelines
from basic building blocks using the bitwise-or (or "pipe" operator)::

    @pipe
    def denoise(value):
        """Denoise uint16 values to 6 significant bits."""
        return value & 0xfc00

    async def main():
        led_brightness = PollADC(26, 0.1) | denoise() | Dedup() | PWMSink(25)
        await asyncio.gather(led_brightness.create_task())
