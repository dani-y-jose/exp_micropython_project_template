import time
from machine import PWM, Pin

from lib.pins import LED, MOTOR_A, MOTOR_B

# DRV8833 one motor: drive IN1 with PWM and hold IN2 low for forward,
# swap which pin carries PWM for reverse. Both low = coast.
STEP = 512
DELAY_MS = 10

in1 = PWM(Pin(MOTOR_A), freq=20000)
in2 = PWM(Pin(MOTOR_B), freq=20000)
led = PWM(Pin(LED), freq=1000)


def drive(duty):
    if duty >= 0:
        in1.duty_u16(duty)
        in2.duty_u16(0)
    else:
        in1.duty_u16(0)
        in2.duty_u16(-duty)
    led.duty_u16(duty if duty >= 0 else -duty)


while True:
    for duty in range(0, 65536, STEP):
        drive(duty)
        time.sleep_ms(DELAY_MS)
    for duty in range(65535, -65536, -STEP):
        drive(duty)
        time.sleep_ms(DELAY_MS)
    for duty in range(-65535, 1, STEP):
        drive(duty)
        time.sleep_ms(DELAY_MS)
