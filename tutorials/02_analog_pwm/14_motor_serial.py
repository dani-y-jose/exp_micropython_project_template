# Host-controllable motor bridge.
#
# Protocol (USB-CDC, line-delimited):
#   host -> board:  a single float per line in [-100.0, +100.0] = % power.
#                   sign encodes direction. clamped. non-numeric lines ignored.
#   board -> host:  CSV. first line is the header; one data line every
#                   REPORT_INTERVAL_MS:
#                       count,revs,angle,rpm,power
#
# By design: NO watchdog. The last commanded power persists until a new
# command arrives or the script is reset. Unplugging the host while the
# motor is running leaves it at the last duty.
#
# Quick test (interactive, mpremote forwards stdin/stdout):
#   uvx mpremote run tutorials/02_analog_pwm/14_motor_serial.py
#   then type "25.0<enter>", "-50.0<enter>", "0<enter>".
#
# Cleaner test from a host Python script — use pyserial: open the port,
# write b"25.0\n", read CSV lines.

import asyncio
import sys
import time
from machine import Pin, PWM

from lib.pins import ENCODER_A, ENCODER_B, MOTOR_A, MOTOR_B

REPORT_INTERVAL_MS = 100
COUNTS_PER_REV = 560   # 7 PPR * 20 gear * 4x quadrature

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

# --- Motor: DRV8833 sign-encoded PWM, same shape as drive() in 08_drv8833_motor.py
in1 = PWM(Pin(MOTOR_A), freq=20000)
in2 = PWM(Pin(MOTOR_B), freq=20000)
current_power = 0.0


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
            pass  # ignore junk so terminal echo / shell prompts don't crash us


async def reporter():
    sys.stdout.write("count,revs,angle,rpm,power\n")
    last_count = 0
    last_ms = time.ticks_ms()
    while True:
        await asyncio.sleep_ms(REPORT_INTERVAL_MS)
        snap = count                                  # snapshot the IRQ-updated value
        now_ms = time.ticks_ms()
        dt_ms = time.ticks_diff(now_ms, last_ms)
        if dt_ms > 0:
            rpm = (snap - last_count) / COUNTS_PER_REV * 60_000 / dt_ms
        else:
            rpm = 0.0
        revs = snap / COUNTS_PER_REV
        angle = (snap % COUNTS_PER_REV) * 360 / COUNTS_PER_REV
        sys.stdout.write("{},{:.4f},{:.2f},{:.2f},{:.2f}\n".format(
            snap, revs, angle, rpm, current_power))
        last_count = snap
        last_ms = now_ms


async def main():
    await asyncio.gather(reader(), reporter())


try:
    asyncio.run(main())
finally:
    # Coast on any exit (KeyboardInterrupt, unhandled exception).
    in1.duty_u16(0)
    in2.duty_u16(0)
