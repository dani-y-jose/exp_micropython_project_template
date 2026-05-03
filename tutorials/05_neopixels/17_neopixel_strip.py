import time
import neopixel
from machine import Pin

from lib.pins import NEOPIXEL

NUM_PIXELS = 8         # set to your strip length
BRIGHTNESS = 0.15      # keep low — full-white draws ~60mA per pixel

np = neopixel.NeoPixel(Pin(NEOPIXEL), NUM_PIXELS)


def hsv(h, s, v):
    # h, s, v in 0..1; returns an (r, g, b) tuple in 0..255.
    i = int(h * 6) % 6
    f = h * 6 - int(h * 6)
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)
    rgb = [(v, t, p), (q, v, p), (p, v, t),
           (p, q, v), (t, p, v), (v, p, q)][i]
    return (int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))


step = 0
while True:
    for i in range(NUM_PIXELS):
        hue = ((step + i) % NUM_PIXELS) / NUM_PIXELS
        np[i] = hsv(hue, 1.0, BRIGHTNESS)
    np.write()
    step += 1
    time.sleep_ms(80)
