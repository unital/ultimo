===============
Display Classes
===============

.. currentmodule:: ultimo_display

The classes definied in :py:mod:`ultimo_display` handle interaction with
display devices attached to the microcontroller.  Since these devices are
diverse, the package is more of a framework for writing compatible devices
than a collection of concrete implementations.

The package provides two classes: an abstract base class
:py:class:`text_device.ATextDevice` and a concrete framebuffer-based
implementation :py:class:`framebuffer_text_device.FrameBufferTextDevice`.

..  warning::

    This API may change in the future depending on the capabilities of other
    types of display hardware.  In particular, it may grow support for
    drawing text in different colors on displays for which it is appropriate.

Text Devices
------------

.. currentmodule:: ultimo_display.text_device

The concept of an :py:class:`ATextDevice` is that it represents display of
monospaced text in rows and columns which has a cursor that can be displayed.
The API is fairly straightforward, providing methods to display text at a
``(column, row)`` position, erase a number of characters at a ``(column, row)``
position, set the cursor's ``(column, row)`` position, hide the cursor, and
clear the display.

It also provides a :py:meth:`ATextDevice.display_text` method that creates
an Ultimo :py:class:`~ultimo.core.Consumer` that expects strings and displays
the values at a location.

Concrete subclasses will need to provide implementations of most of these
methods, although :py:meth:`ATextDevice.erase` and
:py:meth:`ATextDevice.display_text` have default implementations which may
suffice for many devices.

FrameBuffer Text Devices
------------------------

.. currentmodule:: ultimo_display.framebuffer_text_device

The :py:class:`FrameBufferTextDevice` provides a concrete implementation of
:py:class:`~.text_device.ATextDevice` using a :py:class:`framebuf.FrameBuffer`
or another object which implements the same API.

It expects to be provided with an already-allocated buffer of the appropriate
size for the number of rows and columns, and the pixel depth, along with the
size of the display in characters, the pixel format, and optional background
and foreground colors.

..  warning::

    The :py:class:`FrameBufferTextDevice` has not been extensively tested.
