import time
from machine import Pin

from lib.pins import BUTTON

DEBOUNCE_MS = 50

button = Pin(BUTTON, Pin.IN, Pin.PULL_UP)

last_state = button.value()
last_change = time.ticks_ms()

print("press the button (idle =", last_state, ")")

while True:
    state = button.value()
    if state != last_state and time.ticks_diff(time.ticks_ms(), last_change) > DEBOUNCE_MS:
        last_state = state
        last_change = time.ticks_ms()
        print("pressed" if state == 0 else "released")
    time.sleep_ms(5)
