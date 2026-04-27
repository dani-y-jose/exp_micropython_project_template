import machine
import neopixel
import time

DATA_PIN = 14
NUM_LEDS = 25

pin = machine.Pin(DATA_PIN, machine.Pin.OUT)
np = neopixel.NeoPixel(pin, NUM_LEDS)

print("debugging...")

while True:
    # 1. Set the first LED (index 0) to Red. 
    # Format is (Red, Green, Blue) from 0 to 255.
    # WARNING: 255 is blindingly bright. Stick to 10-30 for testing.
    np[0] = (0, 20, 0) 
    
    # 2. Push the data to the hardware
    np.write() 
    print("Blink: RED")
    time.sleep(0.1)

    # 3. Turn it off (0, 0, 0)
    np[0] = (0, 0, 0)
    np.write()
    print("Blink: OFF")
    time.sleep(0.1)