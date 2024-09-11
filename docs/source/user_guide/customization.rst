=============
Customization
=============

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

