""" Echo Input to Output

This example shows how to use a stream to asynchronously read and write.
"""

import uasyncio

from ultimo.core import aconnect
from ultimo.stream import AWrite, ARead


async def main():
    """Read from standard input and echo to standard output."""

    input = ARead()
    output = AWrite()
    task = uasyncio.create_task(aconnect(input, output))
    await uasyncio.gather(task)


if __name__ == '__main__':
    # run forever
    uasyncio.run(main())

