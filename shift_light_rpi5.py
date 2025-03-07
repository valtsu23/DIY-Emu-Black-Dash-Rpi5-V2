import board
import time
import adafruit_pixelbuf
from adafruit_raspberry_pi5_neopixel_write import neopixel_write

NEOPIXEL = board.D21
NUM_PIXELS = 8

class Pi5Pixelbuf(adafruit_pixelbuf.PixelBuf):
    def __init__(self, pin, size, **kwargs):
        self._pin = pin
        super().__init__(size=size, **kwargs)

    def _transmit(self, buf):
        neopixel_write(self._pin, buf)

pixels = Pi5Pixelbuf(NEOPIXEL, NUM_PIXELS, auto_write=True, byteorder="BGR")

# Turn off all the leds
def leds_off():
    pixels.fill((0, 0, 0))

# Blink frequency and timer
BLINK = .1
t1 = time.monotonic()

# Needed variables
shift_changed = 10

def action(rpm, STEP, END, br):
    global shift_changed
    global t1
    shift = (END - rpm) // STEP + 1
    # Blinker
    if rpm > END + STEP:
        if t1 + BLINK < time.monotonic():
            pixels.fill((0, br, br))
        if t1 + BLINK * 2 < time.monotonic():
            pixels.fill((0, 0, 0))
            t1 = time.monotonic()
    # If shift light step is exceeded
    elif shift_changed != shift:
        # LED steps control
        print("Shift:", shift)
        print("Shift_changed:", shift_changed)
        if shift <= 3:
            pixels[0] = (0, br, 0)
            pixels[7] = (0, br, 0)
        else:
            pixels[0] = (0, 0, 0)
            pixels[7] = (0, 0, 0)

        if shift <= 2:
            pixels[1] = (0, br, 0)
            pixels[6] = (0, br, 0)
        else:
            pixels[1] = (0, 0, 0)
            pixels[6] = (0, 0, 0)

        if shift <= 1:
            pixels[2] = (br, br, 0)
            pixels[5] = (br, br, 0)
        else:
            pixels[2] = (0, 0, 0)
            pixels[5] = (0, 0, 0)

        if shift <= 0:
            pixels[3] = (br, 0, 0)
            pixels[4] = (br, 0, 0)
        else:
            pixels[3] = (0, 0, 0)
            pixels[4] = (0, 0, 0)

    # Save the new state
    shift_changed = shift

