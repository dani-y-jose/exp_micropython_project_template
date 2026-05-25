import array
import time
import micropython
from machine import Pin
from micropython import const

from lib.pins import ENCODER_A, ENCODER_B

# Option C: hard IRQ + @micropython.viper. The handler compiles to native
# ARM code, drops per-edge cost from ~10-30 µs (plain Python hard IRQ) to
# ~1-3 µs, and reads pin state directly from the RP2040 GPIO_IN register
# (skipping the Pin.value() Python call).
#
# Viper restrictions: only int/uint/ptr* types inside the function body,
# no high-level Python features. State is kept in a pre-allocated
# array.array so viper can index it via ptr32.
COUNTS_PER_REV = 560

# RP2040 SIO_GPIO_IN register — bit N reflects current input level of GPIO N.
_GPIO_IN = const(0xD0000004)

# Shared state. Layout chosen so viper accesses it as ptr32 with literal indices.
#   _state[0] = count (signed)
#   _state[1] = last_ab (0..3)
#   _state[2] = bit position of ENCODER_A in GPIO_IN
#   _state[3] = bit position of ENCODER_B in GPIO_IN
_state = array.array("i", [0, 0, ENCODER_A, ENCODER_B])

_table = array.array("i", (0, -1, +1, 0,
                           +1, 0, 0, -1,
                           -1, 0, 0, +1,
                           0, +1, -1, 0))

a = Pin(ENCODER_A, Pin.IN, Pin.PULL_UP)
b = Pin(ENCODER_B, Pin.IN, Pin.PULL_UP)
_state[1] = (a.value() << 1) | b.value()


@micropython.viper
def on_edge(pin):
    state = ptr32(_state)
    table = ptr32(_table)
    gpio = ptr32(uint(_GPIO_IN))
    raw = int(gpio[0])
    a_val = (raw >> state[2]) & 1
    b_val = (raw >> state[3]) & 1
    new_ab = (a_val << 1) | b_val
    state[0] = state[0] + table[(state[1] << 2) | new_ab]
    state[1] = new_ab


a.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=on_edge, hard=True)
b.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=on_edge, hard=True)

last_count = 0
last_ms = time.ticks_ms()

while True:
    time.sleep_ms(500)
    now_ms = time.ticks_ms()
    now_count = _state[0]
    dt = time.ticks_diff(now_ms, last_ms) / 1000
    rpm = (now_count - last_count) / COUNTS_PER_REV / dt * 60
    revs = now_count / COUNTS_PER_REV
    print("count={:6d}  revs={:+7.3f}  rpm={:+7.1f}".format(now_count, revs, rpm))
    last_count = now_count
    last_ms = now_ms
