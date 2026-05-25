# Live motor-position gauge.
# Combines the hard-IRQ quadrature decoder from
# tutorials/02_analog_pwm/11_encoder_hard_irq.py with the ST7789 display.
# Needle angle = position within the current revolution.
# Color changes with direction; readouts show total count, revs, and RPM.

import math
import time
import framebuf
from machine import Pin, SPI

from lib.pins import (
    ENCODER_A, ENCODER_B,
    ST7789_SPI_ID, ST7789_SCK, ST7789_MOSI, ST7789_CS, ST7789_DC, ST7789_BL,
    ST7789_WIDTH, ST7789_HEIGHT,
)
from lib.st7789 import ST7789, color565

# Chihai CHR-16GR-050 i20: 7 PPR × 20 gear × 4x quadrature = 560.
COUNTS_PER_REV = 560

QUAD_TABLE = (0, -1, +1, 0,
              +1, 0, 0, -1,
              -1, 0, 0, +1,
              0, +1, -1, 0)

# --- Encoder: hard IRQ, identical pattern to 11_encoder_hard_irq.py -----
a_pin = Pin(ENCODER_A, Pin.IN, Pin.PULL_UP)
b_pin = Pin(ENCODER_B, Pin.IN, Pin.PULL_UP)
count = 0
last_ab = (a_pin.value() << 1) | b_pin.value()


def on_edge(pin):
    global count, last_ab
    new_ab = (a_pin.value() << 1) | b_pin.value()
    count += QUAD_TABLE[(last_ab << 2) | new_ab]
    last_ab = new_ab


a_pin.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=on_edge, hard=True)
b_pin.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=on_edge, hard=True)

# --- Display ------------------------------------------------------------
spi = SPI(ST7789_SPI_ID, baudrate=31_250_000, polarity=0, phase=0,
          sck=Pin(ST7789_SCK), mosi=Pin(ST7789_MOSI))
lcd = ST7789(spi, cs=ST7789_CS, dc=ST7789_DC, bl=ST7789_BL,
             width=ST7789_WIDTH, height=ST7789_HEIGHT)
lcd.set_backlight(40000)

buf = bytearray(ST7789_WIDTH * ST7789_HEIGHT * 2)
fb = framebuf.FrameBuffer(buf, ST7789_WIDTH, ST7789_HEIGHT, framebuf.RGB565)

BG         = color565(0, 0, 20)
DIAL_RING  = color565(100, 100, 130)
DIAL_FILL  = color565(25, 25, 50)
TICK       = color565(180, 180, 200)
NEEDLE_FWD = color565(0, 220, 255)
NEEDLE_REV = color565(255, 100, 0)
TEXT       = color565(255, 255, 255)
DIM        = color565(160, 160, 180)

CX, CY = 120, 100
R = 80
TICK_IN = 68

# Tick mark positions every 30°, pre-computed as (cos, sin) with 0°
# pointing up so the needle's frame of reference matches the user's.
TICKS = []
for deg in range(0, 360, 30):
    rad = math.radians(deg) - math.pi / 2
    TICKS.append((math.cos(rad), math.sin(rad)))

last_count = 0
last_ms = time.ticks_ms()
rpm = 0.0

while True:
    now_count = count                          # snapshot the IRQ-updated value
    now_ms = time.ticks_ms()
    dt_ms = time.ticks_diff(now_ms, last_ms)
    if dt_ms >= 100:
        rpm = (now_count - last_count) / COUNTS_PER_REV * 60_000 / dt_ms
        last_count = now_count
        last_ms = now_ms

    revs = now_count / COUNTS_PER_REV
    pos_in_rev = (now_count % COUNTS_PER_REV) / COUNTS_PER_REV
    angle = pos_in_rev * 2 * math.pi - math.pi / 2
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    needle_color = NEEDLE_REV if rpm < -1 else NEEDLE_FWD

    fb.fill(BG)
    fb.text("motor position", 64, 6, TEXT)

    # Dial face
    fb.ellipse(CX, CY, R, R, DIAL_FILL, True)
    fb.ellipse(CX, CY, R, R, DIAL_RING)

    # Tick marks
    for tcos, tsin in TICKS:
        fb.line(CX + int(TICK_IN * tcos), CY + int(TICK_IN * tsin),
                CX + int(R * tcos),       CY + int(R * tsin), TICK)

    # Needle: a line to a small filled dot at the tip, plus a center hub.
    nx = CX + int((R - 10) * cos_a)
    ny = CY + int((R - 10) * sin_a)
    fb.line(CX, CY, nx, ny, needle_color)
    fb.ellipse(nx, ny, 4, 4, needle_color, True)
    fb.ellipse(CX, CY, 7, 7, needle_color, True)

    # Readouts: three columns of 80 px across the bottom.
    fb.text("count", 16, 192, DIM)
    fb.text("{:>+7d}".format(now_count), 8, 210, TEXT)
    fb.text("revs", 104, 192, DIM)
    fb.text("{:>+7.2f}".format(revs), 88, 210, TEXT)
    fb.text("rpm", 192, 192, DIM)
    fb.text("{:>+6.1f}".format(rpm), 176, 210, TEXT)

    lcd.show(buf)
