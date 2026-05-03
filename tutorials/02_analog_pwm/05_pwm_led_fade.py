import time
from machine import PWM, Pin

from lib.pins import PWM_LED

STEP = 1024
DELAY_MS = 10

pwm = PWM(Pin(PWM_LED), freq=1000)

while True:
    for duty in range(0, 65536, STEP):
        pwm.duty_u16(duty)
        time.sleep_ms(DELAY_MS)
    for duty in range(65535, -1, -STEP):
        pwm.duty_u16(duty)
        time.sleep_ms(DELAY_MS)
