import math
import time
import neopixel
from machine import Pin

from lib.pins import MATRIX_PIN, MATRIX_WIDTH, MATRIX_HEIGHT

NUM_LEDS = MATRIX_WIDTH * MATRIX_HEIGHT
np = neopixel.NeoPixel(Pin(MATRIX_PIN), NUM_LEDS)

CENTER_X = (MATRIX_WIDTH - 1) / 2
CENTER_Y = (MATRIX_HEIGHT - 1) / 2
PEAK = (60, 0, 30)        # ring color at full intensity
RING_WIDTH = 1.0
MAX_RADIUS = max(MATRIX_WIDTH, MATRIX_HEIGHT) / 2 + 1


def xy(x, y):
    if y % 2 == 0:
        return y * MATRIX_WIDTH + x
    return y * MATRIX_WIDTH + (MATRIX_WIDTH - 1 - x)


# Pre-compute distance from center for every pixel — runs once, saves work
# inside the animation loop where 60fps adds up.
DIST = [
    [math.sqrt((x - CENTER_X) ** 2 + (y - CENTER_Y) ** 2) for x in range(MATRIX_WIDTH)]
    for y in range(MATRIX_HEIGHT)
]


def render(radius, intensity):
    for y in range(MATRIX_HEIGHT):
        for x in range(MATRIX_WIDTH):
            d = DIST[y][x] - radius
            falloff = math.exp(-(d * d) / (RING_WIDTH * RING_WIDTH))
            v = intensity * falloff
            np[xy(x, y)] = (int(PEAK[0] * v), int(PEAK[1] * v), int(PEAK[2] * v))
    np.write()


def pulse(duration_s, peak_intensity, steps=18):
    dt = duration_s / steps
    for i in range(steps):
        progress = i / (steps - 1)
        radius = progress * MAX_RADIUS
        intensity = peak_intensity * (1.0 - 0.5 * progress)  # fade as it expands
        render(radius, intensity)
        time.sleep(dt)


while True:
    pulse(0.4, peak_intensity=0.6)
    render(MAX_RADIUS + 2, 0.0)         # clear
    time.sleep(0.6)
