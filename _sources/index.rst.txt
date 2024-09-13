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
application.

In addition to the making the code simpler, this permits updates to be
generated and handled at different rates depending on the needs of the
activity, so a user interaction, like changing the value of a potentiometer or
polling a button can happen in milliseconds, while a clock or temperature
display can be updated much less frequently.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   user_guide.rst
   api.rst

