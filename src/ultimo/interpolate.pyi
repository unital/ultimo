# SPDX-FileCopyrightText: 2024-present Unital Software <info@unital.dev>
#
# SPDX-License-Identifier: MIT

"""Utility interpolation functions"""

from typing import TypeVar, SupportsFloat

value = TypeVar("value")


def linear(x: value, y: value, t: SupportsFloat) -> value:
    """Linear interpolation between x and y."""
