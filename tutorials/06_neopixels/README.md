# 06 — NeoPixels & LED Matrix

Sections 1-5 covered MCU peripherals (including the LCD in section 04). This section is a deep dive into one specific kind of output device that's everywhere in maker projects: **addressable RGB LEDs**, also known as NeoPixels (Adafruit's brand name) or by the chip name **WS2812** (and the slightly-newer SK6812 variant).

We start with one pixel, then a strip, then a 2D matrix, then animations on the matrix.

## Concepts

### What is a NeoPixel?

A WS2812 is a single RGB LED with a tiny controller chip baked in. It has four pins: VCC (5 V), GND, DIN (data in), DOUT (data out). You **daisy-chain** them — DOUT of pixel 1 connects to DIN of pixel 2, and so on. From the MCU's perspective, you're driving one data wire that controls hundreds of pixels.

The catch: the protocol is timing-critical. Each bit is encoded as a high-low pulse pair where the *ratio* matters down to ~150 ns. CPython couldn't dream of doing this in pure software. MicroPython hides it behind a built-in module:

```python
import neopixel
from machine import Pin

np = neopixel.NeoPixel(Pin(14), 8)   # 8 pixels on GPIO 14
np[0] = (32, 0, 0)                   # first pixel: dim red
np.write()                           # latch all pixels
```

`np[i] = (r, g, b)` updates the in-memory buffer — nothing happens on the wire until you call `np.write()`.

### RGB tuples and brightness

Each channel is 0-255. There's no separate brightness control — to dim a pixel, scale the values down. `(255, 255, 255)` is full white at maximum brightness; `(32, 32, 32)` is the same color at ~1/8 brightness. Don't run a strip at full white unless you really need to (see "power" below).

### HSV → RGB for color cycling

Scaling RGB tuples works for one color, but to *cycle* colors smoothly you want **HSV** (hue, saturation, value). Hue is an angle 0-360°; sweeping it through a full turn gives a clean rainbow. MicroPython doesn't ship `colorsys`, so the standard trick is a 12-line conversion function:

```python
def hsv(h, s, v):
    i = int(h * 6) % 6
    f = h * 6 - int(h * 6)
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)
    return [(v, t, p), (q, v, p), (p, v, t),
            (p, q, v), (t, p, v), (v, p, q)][i]
```

`h, s, v` are all 0.0-1.0 floats. Multiply the result by 255 to feed `np[i]`.

### Power and current

Each WS2812 can pull up to **60 mA** at full white. A 64-pixel matrix at full white: ~4 A. Real-world rules of thumb:

- A USB port (500 mA) handles ~10 pixels at full brightness, or 30 pixels at typical "rainbow" brightness.
- Always run a 5 V supply rated for at least `pixels × 60 mA × 1.2`.
- Add a **470 µF capacitor** between V+ and GND near the first pixel to absorb in-rush spikes.
- Put a **330 Ω resistor** in series with the data line (between MCU and DIN) to reduce ringing.

For a single pixel or a 5×5 / 8×8 matrix at the dim brightness levels these tutorials use, USB is fine.

### Matrix wiring: serpentine layout

A 5×5 or 8×8 matrix is logically a 2D grid, but physically it's still a single chain of pixels. Most matrices wire in **serpentine** (also called "boustrophedon") — pixel 0 is top-left, the chain runs right across row 0, then *reverses* across row 1, then right again across row 2, etc.

```
8×8 serpentine:
  row 0:   0  1  2  3  4  5  6  7   →
  row 1:  15 14 13 12 11 10  9  8   ←
  row 2:  16 17 18 19 20 21 22 23   →
  row 3:  31 30 29 28 27 26 25 24   ←
  ...
```

To turn a logical (x, y) into a chain index, you handle the direction flip per row:

```python
def xy(x, y):
    if y % 2 == 0:
        return y * WIDTH + x
    return y * WIDTH + (WIDTH - 1 - x)
```

Some matrices wire row-major (no reversal) or column-major. If your matrix lights up the wrong cell, check the orientation with [18_matrix_xy.py](18_matrix_xy.py) — it puts a different color at each corner so you can see exactly which way is up.

## Wiring

### Single pixel (script 16)

Onboard if you have an RP2040-Zero (GP16) or ESP32-S3 dev board with a built-in pixel. Otherwise:

```
  3V3 / 5V ── VCC
  MCU pin  ── DIN
  GND      ── GND
```

### Strip (script 17)

Same as single — daisy-chained pixels look like one logical "strip" on one data pin. Set `NUM_PIXELS` in the script to match your hardware.

### Matrix (scripts 18-20)

Same wiring as a strip — the matrix is internally one long chain. The board datasheet tells you the layout (serpentine vs row-major) and the data pin. For Waveshare RP2040-Matrix it's GP16; for ESP32-S3-Matrix it's GPIO 14. Both default in [lib/pins.py](../../lib/pins.py).

## Board notes

- **Waveshare RP2040-Zero**: single onboard NeoPixel on GP16, no matrix.
- **Waveshare RP2040-Matrix**: 5×5 matrix on GP16, serpentine.
- **ESP32-S3-Matrix**: 8×8 matrix on GPIO 14, serpentine.
- **Generic ESP32 / Pico**: no onboard NeoPixel — wire one externally to the configured pin.
- **PIO alternative on RP2040**: [display/rp2040_matrix_pio.py](../../display/rp2040_matrix_pio.py) shows how to drive a matrix from a PIO state machine instead of the built-in `neopixel` module. Identical visual result, but the bit-banging happens in PIO hardware so the CPU is free.

## Try changing

- `16_neopixel_blink.py`: replace the R/G/B sequence with an HSV sweep that cycles through every hue.
- `17_neopixel_strip.py`: bounce the pixel back and forth instead of wrapping; add a fading trail.
- `18_matrix_xy.py`: if a corner ends up in the wrong place, your matrix isn't serpentine — try flipping the `if y % 2 == 0` branch or swapping x and y in the `xy()` formula.
- `19_matrix_scan.py`: light the *whole row* at once instead of a single pixel — confirm row order matches your expectation.
- `20_matrix_animation.py`: change `PEAK` to a different color, or replace the Gaussian falloff with a hard ring (`abs(d) < 0.6`).
