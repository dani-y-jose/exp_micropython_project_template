import time
from machine import PWM, Pin

from lib.pins import SERVO

# Servo pulse width in microseconds at 0° and 180°. Calibrate to your servo.
MIN_US = 1000
MAX_US = 2000
PERIOD_US = 20000  # 50 Hz

servo = PWM(Pin(SERVO), freq=50)


def write_angle(deg):
    deg = max(0, min(180, deg))
    pulse_us = MIN_US + (MAX_US - MIN_US) * deg // 180
    servo.duty_u16(pulse_us * 65535 // PERIOD_US)


while True:
    for angle in range(0, 181, 5):
        write_angle(angle)
        time.sleep_ms(20)
    for angle in range(180, -1, -5):
        write_angle(angle)
        time.sleep_ms(20)
