# Serial-controlled motor with a live bipolar RPM gauge on the LCD.
# Combines tutorials/02_analog_pwm/14_motor_serial.py (serial protocol)
# with the gauge style from 05_encoder_gauge.py — but the needle tracks
# RPM rather than absolute position, so the gauge sweeps a half-circle
# from -MAX_RPM (left) through 0 (top) to +MAX_RPM (right).
#
# Protocol (USB-CDC, line-delimited):
#   host -> board:  one float per line, [-100.0, +100.0] % power
#   board -> host:  CSV — count,revs,angle,rpm,power
#
# Three asyncio tasks share the encoder/motor state via module globals.
# A render task redraws the LCD every RENDER_INTERVAL_MS; the SPI burst
# (~50 ms) briefly stalls the event loop, which is why the report cadence
# (100 ms) holds even though both tasks run on a single core.

import asyncio
import math
import sys
import time
import framebuf
from machine import Pin, PWM, SPI

from lib.pins import (
    ENCODER_A, ENCODER_B, MOTOR_A, MOTOR_B,
    ST7789_SPI_ID, ST7789_SCK, ST7789_MOSI, ST7789_CS, ST7789_DC, ST7789_BL,
    ST7789_WIDTH, ST7789_HEIGHT,
)
from lib.st7789 import ST7789, color565

REPORT_INTERVAL_MS = 100
RENDER_INTERVAL_MS = 100
COUNTS_PER_REV = 560
MAX_RPM_DISPLAY = 500   # gauge range; tune to your motor's loaded max

# --- Encoder: hard IRQ, identical pattern to 11_encoder_hard_irq.py -----
QUAD_TABLE = (0, -1, +1, 0,
              +1, 0, 0, -1,
              -1, 0, 0, +1,
              0, +1, -1, 0)

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

# --- Motor (DRV8833) ---------------------------------------------------
in1 = PWM(Pin(MOTOR_A), freq=20000)
in2 = PWM(Pin(MOTOR_B), freq=20000)
current_power = 0.0
current_rpm = 0.0


def apply_power(power):
    global current_power
    if power > 100.0:
        power = 100.0
    elif power < -100.0:
        power = -100.0
    current_power = power
    duty = int(abs(power) * 65535 / 100)
    if power >= 0:
        in1.duty_u16(duty)
        in2.duty_u16(0)
    else:
        in1.duty_u16(0)
        in2.duty_u16(duty)


# --- Display setup -----------------------------------------------------
spi = SPI(ST7789_SPI_ID, baudrate=31_250_000, polarity=0, phase=0,
          sck=Pin(ST7789_SCK), mosi=Pin(ST7789_MOSI))
lcd = ST7789(spi, cs=ST7789_CS, dc=ST7789_DC, bl=ST7789_BL,
             width=ST7789_WIDTH, height=ST7789_HEIGHT)
lcd.set_backlight(40000)

buf = bytearray(ST7789_WIDTH * ST7789_HEIGHT * 2)
fb = framebuf.FrameBuffer(buf, ST7789_WIDTH, ST7789_HEIGHT, framebuf.RGB565)

BG         = color565(0, 0, 20)
ARC_COLOR  = color565(100, 100, 130)
TICK       = color565(180, 180, 200)
NEEDLE_FWD = color565(0, 220, 255)
NEEDLE_REV = color565(255, 100, 0)
ZERO_LINE  = color565(60, 60, 80)
TEXT       = color565(255, 255, 255)
DIM        = color565(160, 160, 180)

CX, CY = 120, 120
R = 85
NEEDLE_R = R - 12

# Pre-compute arc polyline (top half of circle, from -π to 0).
ARC_SEGMENTS = 32
ARC_POINTS = []
for i in range(ARC_SEGMENTS + 1):
    a = -math.pi + i * math.pi / ARC_SEGMENTS
    ARC_POINTS.append((CX + int(R * math.cos(a)),
                       CY + int(R * math.sin(a))))

# Pre-compute tick marks at -MAX, -MAX/2, 0, +MAX/2, +MAX.
TICK_R_IN = R - 10
TICKS = []
for rpm_value in (-MAX_RPM_DISPLAY, -MAX_RPM_DISPLAY // 2, 0,
                  MAX_RPM_DISPLAY // 2, MAX_RPM_DISPLAY):
    frac = rpm_value / MAX_RPM_DISPLAY
    a = -math.pi / 2 + frac * math.pi / 2
    ca, sa = math.cos(a), math.sin(a)
    label = str(rpm_value)
    TICKS.append((
        CX + int(TICK_R_IN * ca), CY + int(TICK_R_IN * sa),
        CX + int(R * ca),         CY + int(R * sa),
        CX + int((R + 10) * ca) - 4 * len(label),
        CY + int((R + 10) * sa) - 4,
        label,
    ))


# --- Async tasks -------------------------------------------------------
async def reader():
    sreader = asyncio.StreamReader(sys.stdin)
    while True:
        line = await sreader.readline()
        if not line:
            continue
        s = line.strip() if isinstance(line, str) else line.decode().strip()
        if not s:
            continue
        try:
            apply_power(float(s))
        except ValueError:
            pass


async def reporter():
    global current_rpm
    sys.stdout.write("count,revs,angle,rpm,power\n")
    last_count = 0
    last_ms = time.ticks_ms()
    while True:
        await asyncio.sleep_ms(REPORT_INTERVAL_MS)
        snap = count
        now_ms = time.ticks_ms()
        dt_ms = time.ticks_diff(now_ms, last_ms)
        if dt_ms > 0:
            rpm = (snap - last_count) / COUNTS_PER_REV * 60_000 / dt_ms
        else:
            rpm = 0.0
        current_rpm = rpm
        revs = snap / COUNTS_PER_REV
        angle_deg = (snap % COUNTS_PER_REV) * 360 / COUNTS_PER_REV
        sys.stdout.write("{},{:.4f},{:.2f},{:.2f},{:.2f}\n".format(
            snap, revs, angle_deg, rpm, current_power))
        last_count = snap
        last_ms = now_ms


async def renderer():
    while True:
        snap_rpm = current_rpm
        snap_power = current_power
        snap_count = count

        if snap_rpm > MAX_RPM_DISPLAY:
            clamped = MAX_RPM_DISPLAY
        elif snap_rpm < -MAX_RPM_DISPLAY:
            clamped = -MAX_RPM_DISPLAY
        else:
            clamped = snap_rpm
        needle_angle = -math.pi / 2 + (clamped / MAX_RPM_DISPLAY) * (math.pi / 2)
        ca, sa = math.cos(needle_angle), math.sin(needle_angle)
        nx = CX + int(NEEDLE_R * ca)
        ny = CY + int(NEEDLE_R * sa)
        needle_color = NEEDLE_REV if snap_rpm < -1 else NEEDLE_FWD

        fb.fill(BG)
        fb.text("motor RPM", 84, 8, TEXT)

        # Half-circle arc + chord
        for i in range(ARC_SEGMENTS):
            x1, y1 = ARC_POINTS[i]
            x2, y2 = ARC_POINTS[i + 1]
            fb.line(x1, y1, x2, y2, ARC_COLOR)
        fb.hline(CX - R, CY, R * 2, ZERO_LINE)

        # Tick marks and labels
        for x1, y1, x2, y2, lx, ly, label in TICKS:
            fb.line(x1, y1, x2, y2, TICK)
            fb.text(label, lx, ly, DIM)

        # Needle
        fb.line(CX, CY, nx, ny, needle_color)
        fb.ellipse(nx, ny, 4, 4, needle_color, True)
        fb.ellipse(CX, CY, 7, 7, needle_color, True)

        # Numeric readouts below the gauge
        fb.text("rpm   {:>+7.1f}".format(snap_rpm),   24, 150, TEXT)
        fb.text("power {:>+7.1f}".format(snap_power), 24, 175, TEXT)
        fb.text("count {:>+7d}".format(snap_count),   24, 200, DIM)

        lcd.show(buf)
        await asyncio.sleep_ms(RENDER_INTERVAL_MS)


async def main():
    await asyncio.gather(reader(), reporter(), renderer())


try:
    asyncio.run(main())
finally:
    in1.duty_u16(0)
    in2.duty_u16(0)
    lcd.fill(color565(0, 0, 0))
