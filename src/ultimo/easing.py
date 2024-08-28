import uasyncio
import utime

from .value import Value


def linear(x, y, t):
    return (1 - t) * x + t * y


class Easing(Value):
    """A class which stores a varying value that can be observed."""

    def __init__(self, value=None, easing=linear, delay=1, rate=0.05):
        super().__init__(value)
        self.target_value = value
        self.last_change = utime.time()
        self.easing = easing
        self.delay = delay
        self.rate = rate
        self.easing_task = None

    async def ease(self):
        while (delta := utime.time() - self.last_change) <= self.delay:
            await uasyncio.sleep(self.rate)
            self.value = self.easing(self.initial_value, self.target_value, delta/self.delay)
            await self.fire()

        self.value = self.target_value
        await self.fire()
        self.easing_task = None

    async def update(self, value):
        if value != self.target_value:
            self.initial_value = value
            self.last_change = utime.time()
            self.target_value = value
            if self.easing_task is None:
                self.easing_task = uasyncio.create_task(self.ease())
