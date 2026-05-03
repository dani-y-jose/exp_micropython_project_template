import time
import neopixel
from machine import Pin

from lib.pins import MATRIX_PIN, MATRIX_WIDTH, MATRIX_HEIGHT

NUM_LEDS = MATRIX_WIDTH * MATRIX_HEIGHT
np = neopixel.NeoPixel(Pin(MATRIX_PIN), NUM_LEDS)


def xy(x, y):
    # Serpentine: row 0 left-to-right, row 1 right-to-left, etc.
    if y % 2 == 0:
        return y * MATRIX_WIDTH + x
    return y * MATRIX_WIDTH + (MATRIX_WIDTH - 1 - x)


# Light up each corner with a different color so you can see the orientation:
#   red    = (0, 0)                                top-left
#   green  = (WIDTH-1, 0)                          top-right
#   blue   = (0, HEIGHT-1)                         bottom-left
#   yellow = (WIDTH-1, HEIGHT-1)                   bottom-right

np.fill((0, 0, 0))
np[xy(0, 0)] = (32, 0, 0)
np[xy(MATRIX_WIDTH - 1, 0)] = (0, 32, 0)
np[xy(0, MATRIX_HEIGHT - 1)] = (0, 0, 32)
np[xy(MATRIX_WIDTH - 1, MATRIX_HEIGHT - 1)] = (32, 32, 0)
np.write()

time.sleep(3)

# Walk a white pixel diagonally to confirm xy() works for both axes.
side = min(MATRIX_WIDTH, MATRIX_HEIGHT)
while True:
    for i in range(side):
        np.fill((0, 0, 0))
        np[xy(i, i)] = (32, 32, 32)
        np.write()
        time.sleep_ms(200)
