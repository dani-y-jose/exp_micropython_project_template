import asyncio
from machine import Pin

from lib.pins import LED, PWM_LED

led_a = Pin(LED, Pin.OUT)
led_b = Pin(PWM_LED, Pin.OUT)   # use as plain digital output here


async def blink(led, period_ms, label):
    while True:
        led.value(not led.value())
        print(label, "toggle")
        await asyncio.sleep_ms(period_ms)


async def main():
    await asyncio.gather(
        blink(led_a, 250, "fast"),
        blink(led_b, 1000, "slow"),
    )


asyncio.run(main())
