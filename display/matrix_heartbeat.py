import machine
import math
import neopixel
import time

DATA_PIN = 14
WIDTH = 8
HEIGHT = 8
NUM_LEDS = WIDTH * HEIGHT

CENTER_X = (WIDTH - 1) / 2
CENTER_Y = (HEIGHT - 1) / 2
PEAK = (80, 0, 0)
RING_WIDTH = 1.2
MAX_RADIUS = 6.0

np = neopixel.NeoPixel(machine.Pin(DATA_PIN, machine.Pin.OUT), NUM_LEDS)


def xy(x, y):
    if y % 2 == 0:
        return y * WIDTH + x
    return y * WIDTH + (WIDTH - 1 - x)


DIST = [
    [math.sqrt((x - CENTER_X) ** 2 + (y - CENTER_Y) ** 2) for x in range(WIDTH)]
    for y in range(HEIGHT)
]


def render(radius, intensity):
    for y in range(HEIGHT):
        for x in range(WIDTH):
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
        # fade the ring as it expands outward
        intensity = peak_intensity * (1.0 - 0.5 * progress)
        render(radius, intensity)
        time.sleep(dt)


while True:
    # lub
    pulse(0.38, peak_intensity=0.1)
    time.sleep(0.08)
    # dub (softer)
    # pulse(0.22, peak_intensity=0.2)
    # rest
    render(MAX_RADIUS + 2, 0.0)
    time.sleep(0.6)
