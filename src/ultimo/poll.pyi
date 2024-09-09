# SPDX-FileCopyrightText: 2024-present Unital Software <info@unital.dev>
#
# SPDX-License-Identifier: MIT

from typing import Any, Callable, Coroutine

from .core import AFlow, ASource, Returned, asynchronize

class PollFlow(AFlow[Returned]):

    source: "Poll"

    def __init__(self, source: "Poll") -> None: ...
    async def __anext__(self) -> Returned: ...

class Poll(ASource[Returned]):

    flow: type[AFlow] = PollFlow

    interval: float

    callback: Callable[[], Coroutine[Any, Any, Returned]]

    def __init__(
        self,
        callback: Callable[[], Coroutine[Any, Any, Returned]],
        interval: float,
    ) -> None: ...

def poll(
    callback: Callable[[], Returned]
) -> Callable[[float], Coroutine[Any, Any, Returned]]: ...
