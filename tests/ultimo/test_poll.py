# SPDX-FileCopyrightText: 2024-present Unital Software <info@unital.dev>
#
# SPDX-License-Identifier: MIT

import unittest
import uasyncio
import utime

from ultimo.poll import Poll, apoll, poll


class TestPoll(unittest.TestCase):

    def test_immediate(self):
        count = 1

        async def decrement():
            nonlocal count
            await uasyncio.sleep(0.001)
            value = count
            count -= 1
            if value < 0:
                return None
            else:
                return value

        source = Poll(decrement, 0.01)

        result = uasyncio.run(source())

        self.assertEqual(result, 1)

    def test_iterate(self):
        count = 10

        async def decrement():
            nonlocal count
            await uasyncio.sleep(0.001)
            value = count
            count -= 1
            if value < 0:
                return None
            else:
                return value

        source = Poll(decrement, 0.01)

        result = []

        async def iterate():
            async for value in source:
                result.append(value)

        start = utime.ticks_ms()
        uasyncio.run(iterate())
        elapsed = utime.ticks_diff(utime.ticks_ms(), start)

        self.assertEqual(result, [10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0])
        self.assertGreaterEqual(elapsed, 100)


    def test_apoll(self):
        count = 10

        @apoll
        async def decrement():
            await uasyncio.sleep(0.001)
            nonlocal count
            value = count
            count -= 1
            if value < 0:
                return None
            else:
                return value

        source = decrement(0.01)

        result = []

        async def iterate():
            async for value in source:
                result.append(value)

        start = utime.ticks_ms()
        uasyncio.run(iterate())
        elapsed = utime.ticks_diff(utime.ticks_ms(), start)

        self.assertEqual(result, [10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0])
        self.assertGreaterEqual(elapsed, 100)


    def test_poll(self):
        count = 10

        @poll
        def decrement():
            nonlocal count
            value = count
            count -= 1
            if value < 0:
                return None
            else:
                return value

        source = decrement(0.01)

        result = []

        async def iterate():
            async for value in source:
                result.append(value)

        start = utime.ticks_ms()
        uasyncio.run(iterate())
        elapsed = utime.ticks_diff(utime.ticks_ms(), start)

        self.assertEqual(result, [10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0])
        self.assertGreaterEqual(elapsed, 100)



if __name__ == "__main__":
    unittest.main()
