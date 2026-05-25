import time
from machine import Pin

from lib.pins import ENCODER_A, ENCODER_B

# Chihai CHR-16GR-050 with 7 PPR Hall encoder, i20 gearbox.
# Counting only rising edges of A gives 7 counts per motor revolution,
# × 20 gear ratio = 140 counts per output-shaft revolution.
COUNTS_PER_REV = 140

a = Pin(ENCODER_A, Pin.IN, Pin.PULL_UP)
b = Pin(ENCODER_B, Pin.IN, Pin.PULL_UP)

count = 0


def on_a_rising(pin):
    global count
    # If B trails A (B low when A rises), the shaft is turning one way;
    # if B leads A (B high), it's the other. Swap the sign if your motor
    # reports negative when you expect positive.
    if b.value():
        count -= 1
    else:
        count += 1


a.irq(trigger=Pin.IRQ_RISING, handler=on_a_rising)

last_count = 0
last_ms = time.ticks_ms()

while True:
    time.sleep_ms(500)
    now_ms = time.ticks_ms()
    now_count = count
    dt = time.ticks_diff(now_ms, last_ms) / 1000
    rpm = (now_count - last_count) / COUNTS_PER_REV / dt * 60
    revs = now_count / COUNTS_PER_REV
    print("count={:6d}  revs={:+7.2f}  rpm={:+7.1f}".format(now_count, revs, rpm))
    last_count = now_count
    last_ms = now_ms
