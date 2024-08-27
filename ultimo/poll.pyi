from typing import Callable, Generic, TypeVar


Returned = TypeVar("Returned")


class PollIter(Generic[Returned]):

    def __init__(self, poll: Callable[[], Returned], interval: float) -> None: ...

    async def __anext__(self) -> Returned: ...


class Poll(Generic[Returned]):

    def __init__(self, callback: Callable[[], Returned], interval: float) -> None: ...

    def __call__(self) -> Returned: ...

    def __ainit__(self) -> PollIter[Returned]: ...
