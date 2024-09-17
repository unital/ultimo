.. Ultimo documentation master file, created by
   sphinx-quickstart on Wed Aug 28 08:27:02 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Ultimo documentation
====================

An interface framework for micropython built around asynchronous iterators.

Ultimo allows you to implement the logic of a micropython application
around a collection of asyncio Tasks that consume asynchronous iterators.
This is compared to the usual synchronous approach of having a single main
loop that mixes together the logic for all the different activities that your
application carries out.

In addition to the making the code simpler, this permits updates to be
generated and handled at different rates depending on the needs of the
activity, so a user interaction, like changing the value of a potentiometer or
polling a button can happen in milliseconds, while a clock or temperature
display can be updated much less frequently.

The :py:mod:`ultimo` library provides classes that simplify this paradigm.
There are classes which provide asynchronous iterators based around polling,
interrupts and asynchronous streams, as well as intermediate transforming
iterators that handle common tasks such as smoothing and de-duplication.
The basic Ultimo library is hardware-independent and should work on any
recent micropython version.

The :py:mod:`ultimo_machine` library provides hardware support wrapping
the micropython :py:mod:`machine`` module and other standard library
modules.  It provides sources for simple polling of, and interrupts from, GPIO
pins, polled ADC, polled RTC, and interrupt-based timer sources.

Ultimo also provides convenience decorators and a pipeline syntax for building
dataflows from basic building blocks.

Ultimo is licensed under the open-source MIT license.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   user_guide.rst
   api.rst

License
-------

MIT License

Copyright (c) 2024 Unital Software

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
