import asyncio
from machine import Pin

from lib.pins import LED

led = Pin(LED, Pin.OUT)


async def blink():
    while True:
        led.value(1)
        await asyncio.sleep_ms(500)
        led.value(0)
        await asyncio.sleep_ms(500)


asyncio.run(blink())
