# Drawing demo for the Waveshare RP2350-Touch-AMOLED-1.43 — 1.43" 466x466
# round AMOLED with a CO5300 (ICNA3311) controller over plain SPI @ 80MHz.
#
# One-time setup. Waveshare's Demo zip ships a MicroPython build with the
# SPI pins/peripherals wired up. The driver itself (amoled_1inch43.py) is
# already vendored into lib/ so Live Run picks it up automatically. Heads
# up: the *V2.0* zip is C-only; you need the older V1 to get the .uf2:
#
#   1. Download:
#      https://files.waveshare.com/wiki/RP2350-Touch-AMOLED-1.43/RP2350-Touch-AMOLED-1.43-Demo.zip
#   2. Flash Python/firmware/RP2350-Touch-AMOLED-1.43.uf2 (hold BOOT, plug
#      USB, drag the .uf2 onto the RPI-RP2 mass-storage drive).
#   3. Run this file with the Live Run task (Cmd+Shift+B).
#
# The driver exposes only set_windows() + flush(bytes) — no draw primitives —
# and a full 466x466 RGB565 framebuffer (434 KB) won't fit in RP2350 SRAM
# (520 KB). So we render into a 16-row framebuf strip and stream the image
# down the panel one strip at a time. framebuf clips out-of-bounds drawing,
# which makes the per-strip code identical to drawing on a full buffer.

import math
import framebuf
from lib.amoled_1inch43 import CO5300

WIDTH = 466
HEIGHT = 466
CX = WIDTH // 2
CY = HEIGHT // 2
STRIP_H = 16  # 466 * 16 * 2 = ~15 KB per strip


# The panel takes RGB565 big-endian; framebuf on RP2 stores native (LE).
# Pre-swapping each colour means framebuf writes the bytes the panel wants —
# no per-pixel swap at flush time.
def _swap(c):
    return ((c & 0xFF) << 8) | (c >> 8)


BLACK = _swap(0x0000)
WHITE = _swap(0xFFFF)
RED = _swap(0xF800)
GREEN = _swap(0x07E0)
BLUE = _swap(0x001F)
YELLOW = _swap(0xFFE0)
CYAN = _swap(0x07FF)


def render_strip(fb, dy):
    fb.fill(BLACK)

    # Twin rings hugging the bezel make the round shape obvious
    fb.ellipse(CX, CY - dy, CX - 2, CY - 2, WHITE)
    fb.ellipse(CX, CY - dy, CX - 8, CY - 8, WHITE)

    # 12 radial tick marks, clock-style
    for i in range(12):
        a = i * math.pi / 6
        sx, sy = math.sin(a), -math.cos(a)
        x0, y0 = CX + int((CX - 16) * sx), CY + int((CY - 16) * sy)
        x1, y1 = CX + int((CX - 40) * sx), CY + int((CY - 40) * sy)
        fb.line(x0, y0 - dy, x1, y1 - dy, CYAN)

    # Concentric target in the middle + horizontal bar through it
    fb.ellipse(CX, CY - dy, 90, 90, BLUE, True)
    fb.ellipse(CX, CY - dy, 60, 60, RED, True)
    fb.ellipse(CX, CY - dy, 30, 30, YELLOW, True)
    fb.fill_rect(CX - 80, CY - 3 - dy, 160, 6, WHITE)

    # 8x8 framebuf font — half a char width per letter for rough centering
    fb.text("RP2350", CX - 24, CY - 130 - dy, GREEN)
    fb.text("AMOLED", CX - 24, CY + 122 - dy, GREEN)


display = CO5300(width=WIDTH, height=HEIGHT, offset_x=6)
display.set_brightness(0xA0)

strip = bytearray(WIDTH * STRIP_H * 2)
fb = framebuf.FrameBuffer(strip, WIDTH, STRIP_H, framebuf.RGB565)
view = memoryview(strip)

y = 0
while y < HEIGHT:
    rows = STRIP_H if y + STRIP_H <= HEIGHT else HEIGHT - y
    render_strip(fb, y)
    display.set_windows(0, y, WIDTH - 1, y + rows - 1)
    display.flush(view[: WIDTH * rows * 2])
    y += rows
