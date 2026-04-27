import machine
import neopixel
import time

DATA_PIN = 16
WIDTH = 5
HEIGHT = 5
NUM_LEDS = WIDTH * HEIGHT

np = neopixel.NeoPixel(machine.Pin(DATA_PIN, machine.Pin.OUT), NUM_LEDS)


# Serpentine wiring: row 0 left-to-right, row 1 right-to-left, etc.
# If your board uses plain row-major wiring, return y * WIDTH + x instead.
def xy(x, y):
    if y % 2 == 0:
        return y * WIDTH + x
    return y * WIDTH + (WIDTH - 1 - x)


def clear():
    for i in range(NUM_LEDS):
        np[i] = (0, 0, 0)


COLORS = [(20, 0, 0), (0, 20, 0), (0, 0, 20)]

while True:
    for color in COLORS:
        for y in range(HEIGHT):
            for x in range(WIDTH):
                clear()
                np[xy(x, y)] = color
                np.write()
                time.sleep(0.05)
