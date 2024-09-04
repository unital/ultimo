# SPDX-FileCopyrightText: 2024-present Unital Software <info@unital.dev>
#
# SPDX-License-Identifier: MIT

"""Utility interpolation functions"""


def linear(x, y, t):
    """Linear interpolation between x and y."""
    return (1 - t) * x + t * y
