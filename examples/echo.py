""" Echo Input to Output

This example shows how to use a stream to asynchronously read and write.
"""

import uasyncio

from ultimo.stream import AWrite, ARead


async def main():
    """Read from standard input and echo to standard output."""

    input = ARead()
    output = AWrite()
    await uasyncio.gather((input | output).create_task())


if __name__ == '__main__':
    # run forever
    uasyncio.run(main())
