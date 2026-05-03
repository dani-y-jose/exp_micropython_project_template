import time
from machine import Pin

from lib.pins import LED

led = Pin(LED, Pin.OUT)

while True:
    led.value(1)
    print("on")
    time.sleep_ms(500)
    led.value(0)
    print("off")
    time.sleep_ms(500)
