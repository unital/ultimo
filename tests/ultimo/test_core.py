# SPDX-FileCopyrightText: 2024-present Unital Software <info@unital.dev>
#
# SPDX-License-Identifier: MIT

import unittest
import uasyncio

from ultimo.core import APipeline, ASource, ASink, asynchronize

class FiniteSource(ASource):

    def __init__(self, count):
        self.count = count

    async def __call__(self):
        await uasyncio.sleep(0.01)
        value = self.count
        self.count -= 1
        if value < 0:
            return None
        else:
            return value

class CollectingSink(ASink):

    def __init__(self, source=None):
        super().__init__(source)
        self.results = []

    async def _process(self, value):
        self.results.append(value)

class IncrementPipeline(APipeline):

    async def _process(self, value):
        return value + 1



class TestASource(unittest.TestCase):

    def test_immediate(self):
        source = FiniteSource(1)

        result = uasyncio.run(source())

        self.assertEqual(result, 1)

    def test_iterate(self):
        source = FiniteSource(10)

        result = []

        async def iterate():
            async for value in source:
                result.append(value)

        uasyncio.run(iterate())

        self.assertEqual(result, [10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0])


class TestASink(unittest.TestCase):

    def test_immediate(self):
        source = FiniteSource(1)
        sink = CollectingSink(source=source)

        uasyncio.run(sink())

        self.assertEqual(sink.results, [1])

    def test_iterate(self):
        source = FiniteSource(10)
        sink = CollectingSink(source=source)

        uasyncio.run(sink.run())

        self.assertEqual(sink.results, [10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0])

    def test_connect(self):
        source = FiniteSource(10)
        sink = CollectingSink()

        uasyncio.run((source | sink).run())

        self.assertEqual(sink.results, [10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0])

    def test_no_source_immediate(self):
        sink = CollectingSink()

        uasyncio.run(sink(1))

        self.assertEqual(sink.results, [1])

    def test_no_source_no_value(self):
        sink = CollectingSink()

        uasyncio.run(sink())

        self.assertEqual(sink.results, [])

    def test_no_source_iterate(self):
        sink = CollectingSink()

        uasyncio.run(sink.run())

        self.assertEqual(sink.results, [])


class TestAPipeline(unittest.TestCase):

    def test_immediate(self):
        source = FiniteSource(1)
        pipeline = IncrementPipeline(source=source)
        sink = CollectingSink(source=pipeline)

        uasyncio.run(sink())

        self.assertEqual(sink.results, [2])

    def test_iterate(self):
        source = FiniteSource(10)
        pipeline = IncrementPipeline(source=source)
        sink = CollectingSink(source=pipeline)

        uasyncio.run(sink.run())

        self.assertEqual(sink.results, [11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1])

    def test_connect(self):
        source = FiniteSource(10)
        pipeline = IncrementPipeline(source=source)
        sink = CollectingSink(source=pipeline)

        uasyncio.run((source | pipeline | sink).run())

        self.assertEqual(sink.results, [11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1])


class TestAsynchronize(unittest.TestCase):

    def test_sync(self):
        def sync_example():
            return 1

        asynchronized = asynchronize(sync_example)

        result = uasyncio.run(asynchronized())

        self.assertEqual(result, 1)


if __name__ == "__main__":
    unittest.main()
