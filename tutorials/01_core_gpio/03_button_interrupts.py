import time
from machine import Pin

from lib.pins import BUTTON

DEBOUNCE_MS = 50

button = Pin(BUTTON, Pin.IN, Pin.PULL_UP)

press_count = 0
last_irq_ms = 0


def on_press(pin):
    # Runs in interrupt context — no print, no allocation, just flag work.
    global press_count, last_irq_ms
    now = time.ticks_ms()
    if time.ticks_diff(now, last_irq_ms) > DEBOUNCE_MS:
        press_count += 1
        last_irq_ms = now


button.irq(trigger=Pin.IRQ_FALLING, handler=on_press)

print("waiting for button presses...")

seen = 0
while True:
    if press_count != seen:
        seen = press_count
        print("press #", seen)
    time.sleep_ms(50)
