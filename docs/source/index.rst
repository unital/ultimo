.. Ultimo documentation master file, created by
   sphinx-quickstart on Wed Aug 28 08:27:02 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Ultimo documentation
====================

An interface framework for micropython built around asynchronous iterators.

Ultimo allows you to implement the logic of a micropython application
around a collection of asyncio Tasks that consume asynchronous iterators.

This is compared to the usual synchronous approach of having an infinite loop
that mixes together the logic for polling of the ADC and clock.

In addition to the code being simpler, this permits updates to be generated
and handled at different rates depending on the needs of the interaction.  For
example, the clock only needs to poll the time occasionally (since it is only
displaying hours and minutes) while the potentiometer needs to be checked
frequently if it is to be responsive to user interactions.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   user_guide.rst
   api.rst

