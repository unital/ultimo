# SPDX-FileCopyrightText: 2024-present Unital Software <info@unital.dev>
#
# SPDX-License-Identifier: MIT

import unittest

from ultimo.interpolate import linear

class TestInterpolate(unittest.TestCase):

    def test_linear(self):
        value = linear(5, 10, 0.5)

        self.assertAlmostEqual(value, 7.5)

if __name__ == "__main__":
    unittest.main()