import time
import rp2
from machine import Pin

from lib.pins import ENCODER_A, ENCODER_B

# Option D: PIO-based encoder. A state machine on one of the RP2040's PIO
# blocks samples the two encoder pins continuously, and pushes the new AB
# state to its RX FIFO only when the state changes. The main CPU does zero
# work per edge — it just drains the FIFO when convenient. This is immune
# to GC pauses up to the FIFO depth.
#
# Requirements: ENCODER_A and ENCODER_B must be consecutive GPIOs
# (in_base=A, then in_(pins, 2) reads A and A+1). On the Pico Explorer
# Base we use GP6 and GP7 — consecutive, good.
#
# Tradeoffs vs maintaining the count inside the PIO itself: that's possible
# but needs a 16-entry computed jump table in PIO asm (~20 instructions).
# This version offloads edge detection only and keeps the math in Python,
# which is still a big win — handler dispatch on every edge is gone.
assert ENCODER_B == ENCODER_A + 1, "PIO in_(pins, 2) requires consecutive GPIOs"

COUNTS_PER_REV = 560

QUAD_TABLE = (0, -1, +1, 0,
              +1, 0, 0, -1,
              -1, 0, 0, +1,
              0, +1, -1, 0)


@rp2.asm_pio(in_shiftdir=rp2.PIO.SHIFT_LEFT,
             fifo_join=rp2.PIO.JOIN_RX)
def quadrature_pio():
    # Y holds the last sampled 2-bit AB state. Initialize to 0; the first
    # real sample will look like a change and push once, which the main
    # loop harmlessly absorbs via the lookup table.
    set(y, 0)
    wrap_target()
    mov(isr, null)          # clear ISR so in_() lands cleanly in low bits
    in_(pins, 2)            # ISR low 2 bits = current AB
    mov(x, isr)             # X = current
    jmp(x_not_y, "changed") # if changed since last sample, push it
    jmp("loop_end")
    label("changed")
    push(noblock)           # send new state to RX FIFO
    mov(y, x)               # remember it
    label("loop_end")
    wrap()


a = Pin(ENCODER_A, Pin.IN, Pin.PULL_UP)
b = Pin(ENCODER_B, Pin.IN, Pin.PULL_UP)

# Sample at ~1 MHz. That's ~250 cycles between samples — orders of magnitude
# faster than the fastest edge rate (~3.7 kHz for this motor), so no edges
# missed. Cranking higher costs power for no benefit here.
sm = rp2.StateMachine(0, quadrature_pio, freq=1_000_000, in_base=a)
sm.active(1)

count = 0
last_ab = (a.value() << 1) | b.value()
last_count = 0
last_ms = time.ticks_ms()

while True:
    # Drain the FIFO frequently. With JOIN_RX the buffer is 8 entries deep,
    # so at 3.7 kHz max edge rate we have ~2 ms of headroom before overflow.
    deadline = time.ticks_add(time.ticks_ms(), 500)
    while time.ticks_diff(deadline, time.ticks_ms()) > 0:
        while sm.rx_fifo() > 0:
            new_ab = sm.get() & 0x3
            count += QUAD_TABLE[(last_ab << 2) | new_ab]
            last_ab = new_ab
        time.sleep_ms(1)

    now_ms = time.ticks_ms()
    dt = time.ticks_diff(now_ms, last_ms) / 1000
    rpm = (count - last_count) / COUNTS_PER_REV / dt * 60
    revs = count / COUNTS_PER_REV
    print("count={:6d}  revs={:+7.3f}  rpm={:+7.1f}".format(count, revs, rpm))
    last_count = count
    last_ms = now_ms
