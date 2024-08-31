from typing import Any, Callable, Generic, TypeVar, Coroutine

from .core import AFlow, ASource, asynchronize, Returned


class PollFlow(AFlow, Generic[Returned]):

    source: "Poll"

    def __init__(self, source: "Poll") -> None: ...

    async def __anext__(self) -> Returned: ...


class Poll(Generic[Returned]):

    flow: type[AFlow] = PollFlow

    interval: float

    callback: Coroutine[Any, Any, Returned]

    def __init__(self, callback: Callable[[], Returned] | Coroutine[Any, Any, Returned], interval: float) -> None: ...

    def __call__(self) -> Returned: ...

    def __ainit__(self) -> PollFlow[Returned]: ...


def poll(callback: Callable[[], Returned]) -> Callable[[float], Coroutine[Any, Any, Returned]]: ...
