# SPDX-FileCopyrightText: 2024-present Unital Software <info@unital.dev>
#
# SPDX-License-Identifier: MIT

import sys
from typing import AnyStr, IO, Self

import uasyncio

from .core import ASink, ASource



class StreamMixin:
    """Mixin that gives async context manager behaviour to close a stream."""

    stream: uasyncio.StreamWriter

    async def __aenter__(self) -> Self: ...

    async def __aexit__(self, *exc) -> bool: ...

    async def close(self) -> None:
        """Close the output stream."""


class AWrite(ASink[AnyStr], StreamMixin):
    """Write to a stream asynchronously."""

    stream: uasyncio.StreamWriter

    def __init__(self, stream: IO[AnyStr] = sys.stdout, source: ASource[AnyStr] | None = None): ...

    async def __call__(self, value: AnyStr | None = None) -> None: ...

    def __ror__(self, other: ASource[AnyStr]) -> AWrite[AnyStr]: ...


class ARead(ASource[AnyStr], StreamMixin):
    """Read from a stream asynchronously one character at a time."""

    stream: uasyncio.StreamReader

    def __init__(self, stream: IO[AnyStr] = sys.stdin): ...

    async def __call__(self) -> AnyStr | None: ...


class AReadline(ASource[str], StreamMixin):
    """Read from a text stream asynchronously one line at a time."""

    stream: uasyncio.StreamReader

    def __init__(self, stream: IO[str] = sys.stdin): ...

    async def __call__(self) -> str | None: ...
