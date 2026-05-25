import asyncio
import time
from machine import Pin

from lib.pins import BUTTON, LED

DEBOUNCE_MS = 50

button = Pin(BUTTON, Pin.IN, Pin.PULL_UP)
led = Pin(LED, Pin.OUT)

# ThreadSafeFlag is the only asyncio primitive safe to call from an IRQ.
press_flag = asyncio.ThreadSafeFlag()


def on_press(pin):
    press_flag.set()


button.irq(trigger=Pin.IRQ_FALLING, handler=on_press)


async def consume_presses():
    count = 0
    last_ms = 0
    while True:
        await press_flag.wait()
        now = time.ticks_ms()
        if time.ticks_diff(now, last_ms) > DEBOUNCE_MS:
            count += 1
            last_ms = now
            print("press #", count)


async def heartbeat():
    while True:
        led.value(not led.value())
        await asyncio.sleep_ms(200)


async def main():
    await asyncio.gather(consume_presses(), heartbeat())


asyncio.run(main())
