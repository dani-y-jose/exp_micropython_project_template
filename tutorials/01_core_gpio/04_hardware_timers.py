import sys
import time
from machine import Pin, Timer

from lib.pins import LED

led = Pin(LED, Pin.OUT)


def toggle(t):
    led.value(not led.value())


# ESP32 uses numbered hardware timers; RP2 takes no ID.
timer = Timer(0) if sys.platform == "esp32" else Timer()
timer.init(period=500, mode=Timer.PERIODIC, callback=toggle)

# Main loop is free to do other work — the LED keeps blinking on its own.
n = 0
while True:
    print("main loop tick", n)
    n += 1
    time.sleep(2)
