========
Examples
========


Putting it all Together
=======================

..  warning::

    This is currently hypothetical.  API may change.

Let's consider a system where we have:

- an lcd with an led backlight which use I2C
- a push button on GPIO pin 0
- a potentiometer on pin 19

and we want the behaviour:

- the push button turns the led and lcd on and off
- the potentiometer controls the brightness of the led
- the lcd displays the current time in minutes

The potentiometer needs its raw value converted to a range 0-255 for the led,
and we only want to change the value when the value actually changes, so we
use::

    @pipe
    def brightness(raw_value):
        return raw_value >> 8

    brightness_task = Task(connect(led.brightness, dedup(brightness(adc(19)))))

The time for the lcd needs formatting and deduplication::

    @pipe
    def hours_minutes(dt):
        return dt[4:6]

    @pipe
    def format(t):
        return b'{0:02}:{1:02}'.format(*t)

    @sink
    def display_bytes(value):
        lcd.clear()
        lcd.write_ddram(value)

    time_task = Task(display_bytes(format(dedup(hours_minutes(poll_rtc(1.0))))

The button is a simple GPIO, but is noisy and needs de-bouncing, so we use
an interrupt::

    async def on_off(button):
        state = False
        async for _ in button:
            state = not state
            if state:
                brightness_task = create_task(connect(led.brightness, dedup(brightness(adc(19)))))
                time_task = create_task(display_bytes(format(dedup(hours_minutes(poll_rtc(1.0))))
            else:
                brightness_task.cancel()
                time_task.cancel()

    async def main():
        button = debounce(button(pin))
        task = Task(on_off(button))
        await gather(task)

    if __name__ == '__main__':
        run(main())

Other Examples
==============

