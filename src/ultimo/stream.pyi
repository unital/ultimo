# SPDX-FileCopyrightText: 2024-present Unital Software <info@unital.dev>
#
# SPDX-License-Identifier: MIT

import sys
from typing import IO, Self

import uasyncio

from .core import ASink, ASource


class AWrite(ASink):
    """Write to a stream asynchronously."""

    stream: uasyncio.StreamWriter

    def __init__(self, stream: IO = sys.stdout, source: ASource = None): ...

    async def __call__(self, value: str | bytes | None = None) -> None: ...

    async def __aenter__(self) -> Self: ...

    async def __aexit__(self, *exc) -> bool: ...

    async def close(self) -> None:
        """Close the output stream."""


class ARead(ASource):
    """Read from a stream asynchronously one character at a time."""

    stream: uasyncio.StreamReader

    def __init__(self, stream: IO = sys.stdin): ...

    async def __call__(self) -> bytes | None: ...

    async def __aenter__(self) -> Self: ...

    async def __aexit__(self, *exc) -> bool: ...

    async def close(self) -> None:
        """Close the output stream."""
