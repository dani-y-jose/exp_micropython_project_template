import time
from machine import Pin

from lib.pins import ENCODER_A, ENCODER_B

# Option B: same algorithm as 10_encoder_read_4x.py, but the IRQ handler
# runs in hard interrupt context (hard=True). Latency drops from ~50-200 µs
# (soft-scheduled, GC-stallable) to ~5-15 µs and is not affected by garbage
# collection in the main loop.
#
# Hard-IRQ restrictions: the handler MUST NOT allocate memory. That means
# no print, no f-strings, no creating tuples/lists/dicts, no float ops that
# box. What's safe here: indexing a pre-allocated tuple, integer math on
# globals, calling pin.value(), assigning to global ints.
COUNTS_PER_REV = 560

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


a.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=on_edge, hard=True)
b.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=on_edge, hard=True)

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
