from machine import I2C
from struct import pack
import utime

from .pca9633 import PCA9633, DEFAULT_ADDRESS as LED_ADDRESS
from .aip31068l import AiP31068L, DEFAULT_ADDRESS as LCD_ADDRESS


class LCD1602_RGB:
    """Driver for Waveshare LCD1602 RGB and similar LCDs with LED backlight."""

    led: PCA9633

    lcd: AiP31068L

    def __init__(self, i2c: I2C):
        self.led = PCA9633(i2c, address=LED_ADDRESS)
        self.lcd = AiP31068L(i2c, address=LCD_ADDRESS)

    def init(self, clear_cgram=False):
        self.lcd.function_set()

        # wait 50 ms and try again
        utime.sleep(0.05)
        self.lcd.function_set()

        # wait 50 ms and try again
        utime.sleep(0.05)
        self.lcd.function_set()

        # clear display, set for left-right languages, and turn off display
        self.lcd.clear()
        self.lcd.entry_mode()
        self.lcd.display_control()

        # clear cgram
        if clear_cgram:
            self.lcd.clear_cgram()

        # blink mode, all off, 100% blink duty cycle, all grouped
        self.led.write_state(b'\x80\x20\x00\x00\x00\x00\xff\x00\xff')

    async def ainit(self, clear_cgram=False):
        import uasyncio

        self.lcd.function_set()

        # wait 50 ms and try again
        await uasyncio.sleep(0.05)
        self.lcd.function_set()

        # wait 50 ms and try again
        await uasyncio.sleep(0.05)
        self.lcd.function_set()

        # clear display, set for left-right languages, and turn off display
        self.lcd.clear()
        self.lcd.entry_mode()
        self.lcd.display_control()

        # clear cgram
        if clear_cgram:
            self.lcd.clear_cgram()

        # blink mode, all off, 100% blink duty cycle, all grouped
        self.led.write_state(b'\x80\x20\x00\x00\x00\x00\xff\x00\xff')

    def set_rgb(self, r: int, g: int, b: int):
        leds = pack("BBB", b, g, r)
        self.led.write_leds(leds)

    def led_white(self):
        self.set_rgb(0xff, 0xff, 0xff)


