import machine
import neopixel
import time

DATA_PIN = 14
NUM_LEDS = 25

np = neopixel.NeoPixel(machine.Pin(DATA_PIN, machine.Pin.OUT), NUM_LEDS)

# WARNING: 255 is blindingly bright. Stick to 10-30 for testing.
COLOR = (0, 20, 0)

while True:
    np[0] = COLOR
    np.write()
    print("on")
    time.sleep(0.5)

    np[0] = (0, 0, 0)
    np.write()
    print("off")
    time.sleep(0.5)
