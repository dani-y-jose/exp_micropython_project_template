import time
import neopixel
from machine import Pin

from lib.pins import MATRIX_PIN, MATRIX_WIDTH, MATRIX_HEIGHT

NUM_LEDS = MATRIX_WIDTH * MATRIX_HEIGHT
np = neopixel.NeoPixel(Pin(MATRIX_PIN), NUM_LEDS)


def xy(x, y):
    if y % 2 == 0:
        return y * MATRIX_WIDTH + x
    return y * MATRIX_WIDTH + (MATRIX_WIDTH - 1 - x)


COLORS = [(32, 0, 0), (0, 32, 0), (0, 0, 32)]
DELAY_MS = 50

color_idx = 0
while True:
    color = COLORS[color_idx]
    for y in range(MATRIX_HEIGHT):
        for x in range(MATRIX_WIDTH):
            np.fill((0, 0, 0))
            np[xy(x, y)] = color
            np.write()
            time.sleep_ms(DELAY_MS)
    color_idx = (color_idx + 1) % len(COLORS)
