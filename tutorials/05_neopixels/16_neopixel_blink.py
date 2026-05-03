import time
import neopixel
from machine import Pin

from lib.pins import NEOPIXEL

np = neopixel.NeoPixel(Pin(NEOPIXEL), 1)

COLORS = [
    (32, 0, 0),    # red
    (0, 32, 0),    # green
    (0, 0, 32),    # blue
    (0, 0, 0),     # off
]

while True:
    for color in COLORS:
        np[0] = color
        np.write()
        print("color:", color)
        time.sleep_ms(500)
