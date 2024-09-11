# SPDX-FileCopyrightText: 2024-present Unital Software <info@unital.dev>
#
# SPDX-License-Identifier: MIT

"""
Echo Input to Output
--------------------

This example shows how to use a stream to asynchronously read and write.
It should work on any device that can connect a serial terminal to
micropython standard input and output.
"""

import uasyncio

from ultimo.stream import ARead, AWrite


async def main():
    """Read from standard input and echo to standard output."""

    echo = ARead() | AWrite()
    await uasyncio.gather(echo.create_task())


if __name__ == "__main__":
    # run forever
    uasyncio.run(main())
