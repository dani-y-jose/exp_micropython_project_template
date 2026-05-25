import time
from machine import Pin

from lib.pins import ENCODER_A, ENCODER_B

# 4x quadrature decoding: count every edge on both A and B.
# 7 PPR × 20 gear ratio × 4 = 560 counts per output-shaft revolution.
COUNTS_PER_REV = 560

# Gray-code transition table indexed by (prev_AB << 2 | new_AB).
# Valid forward transitions: 00→01→11→10→00 → +1 each step.
# Valid reverse transitions: 00→10→11→01→00 → -1 each step.
# Same-state or double-step (illegal/missed edge) entries are 0.
QUAD_TABLE = (0, -1, +1, 0,
              +1, 0, 0, -1,
              -1, 0, 0, +1,
              0, +1, -1, 0)

a = Pin(ENCODER_A, Pin.IN, Pin.PULL_UP)
b = Pin(ENCODER_B, Pin.IN, Pin.PULL_UP)

count = 0
last_ab = (a.value() << 1) | b.value()


def on_edge(pin):
    global count, last_ab
    new_ab = (a.value() << 1) | b.value()
    count += QUAD_TABLE[(last_ab << 2) | new_ab]
    last_ab = new_ab


a.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=on_edge)
b.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=on_edge)

last_count = 0
last_ms = time.ticks_ms()

while True:
    time.sleep_ms(500)
    now_ms = time.ticks_ms()
    now_count = count
    dt = time.ticks_diff(now_ms, last_ms) / 1000
    rpm = (now_count - last_count) / COUNTS_PER_REV / dt * 60
    revs = now_count / COUNTS_PER_REV
    print("count={:6d}  revs={:+7.3f}  rpm={:+7.1f}".format(now_count, revs, rpm))
    last_count = now_count
    last_ms = now_ms
