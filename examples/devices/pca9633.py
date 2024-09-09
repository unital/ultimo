from machine import I2C

DEFAULT_ADDRESS = (0xc0>>1)

MODE1 = 0x00
MODE2 = 0x01
PWM0 = 0x02
PWM1 = 0x03
PWM2 = 0x04
PWM3 = 0x05
GRPPWM = 0x06
GRPFREQ = 0x07
LEDOUT = 0x08

AUTOINCREMENT_ENABLED = 0b10000000
AUTOINCREMENT_BIT1 = 0b01000000
AUTOINCREMENT_BIT0 = 0b00100000

# MODE 1 flags
SLEEP_ON = 0b00010000
SLEEP_OFF = 0b00000000
SUB1_ON = 0b00001000
SUB2_ON = 0b00000100
SUB3_ON = 0b00000010
ALLCALL_ON = 0b00000001
SUB1_OFF = SUB2_OFF = SUB3_OFF = ALLCALL_OFF = 0b00000000

# MODE 2 flags
DIM = 0b00000000
BLINK = 0b00100000
# These depend on physical hardware connections
NOT_INVERTED = 0b00000000
INVERTED = 0b00010000
OCH_STOP = 0b00000000
OCH_ACK = 0b00001000
OUTDRV_OPEN_DRAIN = 0b00000000
OUTDRV_TOTEM_POLE = 0b00000100


class PCA9633:
    """I2C multiple LED controller"""

    i2c: I2C

    address: int

    def __init__(self, i2c: I2C, address: int = DEFAULT_ADDRESS):
        self.i2c = i2c
        self.address = address

    def write_register(self, register: int, data: bytes, flags: int = 0):
        if len(data) > 1 and not (flags & AUTOINCREMENT_ENABLED):
            data = data[:1]
        self.i2c.writeto_mem(self.address, register | flags, data)

    def read_register(self, register: int, size: int = 1, flags: int = 0) -> bytes:
        if size > 1 and not (flags & AUTOINCREMENT_ENABLED):
            size = 1
        return self.i2c.readfrom_mem(self.address, register | flags, size)

    def read_state(self):
        return self.read_register(MODE1, 9, AUTOINCREMENT_ENABLED)

    def write_state(self, state: bytes):
        state = state[:9]
        return self.write_register(MODE1, state, AUTOINCREMENT_ENABLED)

    def write_leds(self, leds: bytes):
        return self.write_register(PWM0, leds, AUTOINCREMENT_ENABLED | AUTOINCREMENT_BIT0)

    @property
    def sleep(self):
        return bool(ord(self.read_register(MODE1)) & SLEEP_ON)

    @sleep.setter
    def sleep(self, sleep: bool = True):
        mode1 = ord(self.read_register(MODE1))
        if sleep:
            data = (mode1 | SLEEP_ON)
        else:
            data = (mode1 & ~SLEEP_ON)
        self.write_register(MODE1, data.to_bytes(1, 'little'))

    def blink(self, period: float = 1.0, ratio: float = 0.5):
        if period == 0:
            freq = 0x00
        else:
            freq = int(period * 24 - 1)
        duty = int(ratio * 255)
        mode2 = ord(self.read_register(MODE2))
        self.write_register(MODE2, (mode2 | BLINK).to_bytes(1, "little"))
        self.write_register(GRPPWM, duty.to_bytes(1, "little"))
        self.write_register(GRPFREQ, freq.to_bytes(1, "little"))

    def dim(self, brightness: float = 1.0):
        value = int(brightness * 255)
        mode2 = ord(self.read_register(MODE2))
        self.write_register(MODE2, (mode2 & ~BLINK).to_bytes(1, "little"))
        self.write_register(GRPPWM, value.to_bytes(1, "little"))
