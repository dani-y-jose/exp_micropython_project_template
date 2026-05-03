import asyncio
import network
import time
from machine import Pin

from lib.pins import LED
from lib.secrets import WIFI_SSID, WIFI_PASSWORD

led = Pin(LED, Pin.OUT)

PAGE = """\
<!doctype html><html><body>
<h2>MicroPython LED (async)</h2>
<p>State: {state}</p>
<p><a href="/on">on</a> | <a href="/off">off</a></p>
</body></html>
"""


def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        deadline = time.time() + 15
        while not wlan.isconnected() and time.time() < deadline:
            time.sleep(0.5)
    if not wlan.isconnected():
        raise RuntimeError("WiFi failed")
    return wlan


async def handle(reader, writer):
    request = await reader.read(1024)
    line = request.decode().split("\r\n", 1)[0]
    if " /on " in line:
        led.value(1)
    elif " /off " in line:
        led.value(0)
    body = PAGE.format(state="on" if led.value() else "off")
    writer.write(b"HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n")
    writer.write(body.encode())
    await writer.drain()
    await writer.wait_closed()


async def heartbeat():
    # Toggle a "loop alive" indicator on stdout — LED is owned by handlers.
    while True:
        print("heartbeat:", time.ticks_ms())
        await asyncio.sleep(2)


async def main():
    wlan = connect_wifi()
    print("open http://" + wlan.ifconfig()[0] + "/  in your browser")
    server = await asyncio.start_server(handle, "0.0.0.0", 80)
    await asyncio.gather(heartbeat(), server.wait_closed())


asyncio.run(main())
