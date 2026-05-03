import asyncio
import dht
from machine import Pin

from lib.pins import I2C_SDA, LED

SAMPLE_INTERVAL_MS = 2000
HEARTBEAT_MS = 250

sensor = dht.DHT22(Pin(I2C_SDA))
led = Pin(LED, Pin.OUT)


async def producer(queue):
    while True:
        sensor.measure()       # ~20ms blocking — short enough to tolerate
        reading = (sensor.temperature(), sensor.humidity())
        await queue.put(reading)
        await asyncio.sleep_ms(SAMPLE_INTERVAL_MS)


async def consumer(queue):
    while True:
        temp, hum = await queue.get()
        print("temp:", temp, "C  humidity:", hum, "%")


async def heartbeat():
    while True:
        led.value(not led.value())
        await asyncio.sleep_ms(HEARTBEAT_MS)


async def main():
    queue = asyncio.Queue()
    await asyncio.gather(producer(queue), consumer(queue), heartbeat())


asyncio.run(main())
