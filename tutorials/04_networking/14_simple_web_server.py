import network
import socket
import time
from machine import Pin

from lib.pins import LED
from lib.secrets import WIFI_SSID, WIFI_PASSWORD

led = Pin(LED, Pin.OUT)

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
if not wlan.isconnected():
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    deadline = time.time() + 15
    while not wlan.isconnected() and time.time() < deadline:
        time.sleep(0.5)

if not wlan.isconnected():
    raise RuntimeError("WiFi failed")

print("open http://" + wlan.ifconfig()[0] + "/  in your browser")

PAGE = """\
<!doctype html><html><body>
<h2>MicroPython LED</h2>
<p>State: {state}</p>
<p><a href="/on">on</a> | <a href="/off">off</a></p>
</body></html>
"""

s = socket.socket()
s.bind(("0.0.0.0", 80))
s.listen(1)

while True:
    conn, addr = s.accept()
    try:
        request = conn.recv(1024).decode()
        line = request.split("\r\n", 1)[0]
        if " /on " in line:
            led.value(1)
        elif " /off " in line:
            led.value(0)
        body = PAGE.format(state="on" if led.value() else "off")
        conn.send(b"HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n")
        conn.send(body.encode())
    finally:
        conn.close()
