import machine
import math
import neopixel
import time

from lib.mesh import MeshNode

DATA_PIN = 14
WIDTH = 8
HEIGHT = 8
NUM_LEDS = WIDTH * HEIGHT

CENTER_X = (WIDTH - 1) / 2
CENTER_Y = (HEIGHT - 1) / 2
RING_WIDTH = 1.2
MAX_RADIUS = 6.0

OK_COLOR = (0, 60, 0)
ALERT_COLOR = (60, 0, 0)

np = neopixel.NeoPixel(machine.Pin(DATA_PIN, machine.Pin.OUT), NUM_LEDS)


def xy(x, y):
    if y % 2 == 0:
        return y * WIDTH + x
    return y * WIDTH + (WIDTH - 1 - x)


DIST = [
    [math.sqrt((x - CENTER_X) ** 2 + (y - CENTER_Y) ** 2) for x in range(WIDTH)]
    for y in range(HEIGHT)
]


def render(radius, intensity, color):
    for y in range(HEIGHT):
        for x in range(WIDTH):
            d = DIST[y][x] - radius
            falloff = math.exp(-(d * d) / (RING_WIDTH * RING_WIDTH))
            v = intensity * falloff
            np[xy(x, y)] = (int(color[0] * v), int(color[1] * v), int(color[2] * v))
    np.write()


def clear():
    for i in range(NUM_LEDS):
        np[i] = (0, 0, 0)
    np.write()


def pulse(color, duration_s=0.25, steps=12):
    dt = duration_s / steps
    for i in range(steps):
        progress = i / (steps - 1)
        radius = progress * MAX_RADIUS
        intensity = 1.0 - 0.5 * progress
        render(radius, intensity, color)
        time.sleep(dt)
    clear()


clear()
mesh = MeshNode("gateway", channel=1)
print("mesh matrix gateway listening on channel 1")

while True:
    pkt = mesh.recv()
    if not pkt:
        continue
    print("rx:", pkt)
    data = pkt.get("data", {})
    status = data.get("status", "ok") if isinstance(data, dict) else "ok"
    pulse(ALERT_COLOR if status == "alert" else OK_COLOR)
