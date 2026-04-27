# PIO assembly inside @rp2.asm_pio uses names (wrap_target, out, jmp, ...)
# that only exist at decorator time, so static analysis can't see them.
# pyright: reportUndefinedVariable=false
"""PIO-driven WS2812 scan on the Waveshare RP2040-Matrix (5x5 on GPIO 16).

Uses the RP2040's PIO unit: a small PIO program implements WS2812 timing in
hardware, and `sm.put()` streams 24-bit GRB pixel data through it. Same
idiom as the upstream MicroPython `pio_ws2812` example, kept here as a
PIO + rp2-stubs smoke test for this template.
"""
import array
import time
import rp2
from machine import Pin

NUM_LEDS = 25
DATA_PIN = 16


@rp2.asm_pio(
    sideset_init=rp2.PIO.OUT_LOW,
    out_shiftdir=rp2.PIO.SHIFT_LEFT,
    autopull=True,
    pull_thresh=24,
)
def ws2812():
    # Bit period = T1 + T2 + T3 = 10 PIO cycles. At freq=8 MHz that's 1.25us,
    # the standard WS2812 bit width.
    T1 = 2
    T2 = 5
    T3 = 3
    wrap_target()
    label("bitloop")
    out(x, 1)               .side(0)    [T3 - 1]
    jmp(not_x, "do_zero")   .side(1)    [T1 - 1]
    jmp("bitloop")          .side(1)    [T2 - 1]
    label("do_zero")
    nop()                   .side(0)    [T2 - 1]
    wrap()


sm = rp2.StateMachine(0, ws2812, freq=8_000_000, sideset_base=Pin(DATA_PIN))
sm.active(1)

pixels = array.array("I", [0] * NUM_LEDS)


def grb(r, g, b):
    # WS2812 expects GRB MSB-first; sm.put(..., 8) shifts these 24 bits to
    # the top of the 32-bit word so the PIO program clocks them out first.
    return (g << 16) | (r << 8) | b


def show():
    sm.put(pixels, 8)


COLORS = [(20, 0, 0), (0, 20, 0), (0, 0, 20)]

while True:
    for r, g, b in COLORS:
        c = grb(r, g, b)
        for i in range(NUM_LEDS):
            for j in range(NUM_LEDS):
                pixels[j] = 0
            pixels[i] = c
            show()
            time.sleep_ms(120)
