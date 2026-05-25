# 05 — Networking & IoT

The first three sections were the MCU talking to wires. This section is the MCU talking to the rest of the world. We connect to WiFi, fetch data from the public internet, host a tiny webpage, and publish sensor readings to an MQTT broker.

These scripts only run on boards with WiFi: **ESP32**, **ESP32-S3/C3**, **Raspberry Pi Pico W**.

## Concepts

### WiFi

Two modes:
- **STA (station)**: the board joins your existing network — what you almost always want.
- **AP (access point)**: the board *is* a network — useful for first-boot configuration UIs.

`12_wifi_connect.py` is the boilerplate every networked sketch starts with: enable the radio, call `connect()`, wait for `isconnected()` with a timeout, retry on failure. Reuse it as the first few lines of every networking script.

### Credentials

Real WiFi/MQTT credentials don't belong in source. The template keeps them in `lib/secrets.py` (gitignored). Copy `lib/secrets_example.py` to start:

```sh
cp lib/secrets_example.py lib/secrets.py
# edit with your real values
```

Scripts then `from lib.secrets import WIFI_SSID, WIFI_PASSWORD`.

### HTTP

`urequests` mirrors Python's `requests`: `urequests.get(url)` returns a response with `.json()` and `.text`. Always call `.close()` to free the socket — MicroPython doesn't garbage-collect them aggressively.

```python
import urequests
r = urequests.get("https://api.example.com/data")
print(r.json())
r.close()
```

ESP32 ships with `urequests` built in. RP2040 needs `mip install urequests`.

### Sockets and a tiny web server

`urequests` is a client. To *serve* a page, you drop down to raw sockets:

```python
import socket
s = socket.socket()
s.bind(("0.0.0.0", 80))
s.listen(1)
conn, addr = s.accept()
request = conn.recv(1024)
conn.send(b"HTTP/1.0 200 OK\r\n\r\n<html>...</html>")
conn.close()
```

`14_simple_web_server.py` parses the request line for `/on` or `/off` and toggles the LED accordingly. Real apps use a framework like `microdot`, but knowing the bare-socket version is worth a tutorial.

### MQTT

Lightweight pub/sub messaging over TCP — the de facto IoT protocol. A **broker** (Mosquitto, EMQX, HiveMQ) is the central server; clients **publish** to topics and **subscribe** to topics. Devices on the same network subscribe to each other through the broker.

```python
from umqtt.simple import MQTTClient
client = MQTTClient("client-id", "broker.local", port=1883)
client.connect()
client.publish(b"sensor/temp", b"22.4")
```

`15_mqtt_publish.py` reads the ADC every 5 s and publishes it to `tutorial/sensor`. Verify with mosquitto on your laptop:

```sh
mosquitto_sub -h <broker> -t tutorial/sensor
```

## Wiring

No new wiring for this section — the LED is already onboard, the ADC reuses section 2's potentiometer.

## Board notes

- **ESP32** family: WiFi power-saves aggressively by default; `wlan.config(pm=0xa11140)` keeps it awake if you see latency. STA + AP modes can run simultaneously if you need both.
- **Pico W**: Uses `network.WLAN(network.STA_IF)` like ESP32; first connection after boot can take 5-10 seconds. `mip install urequests umqtt.simple` are required (built-in on ESP32).
- **Pico (no W)**: No radio — these scripts won't run. Stop at section 3.
- **Brokers**: For local testing, Mosquitto on `192.168.1.x` or your laptop is easiest. For internet-exposed brokers, use TLS (`umqtt.simple` supports `ssl=True`) and rotate credentials.

## Try changing

- `12_wifi_connect.py`: drop the SSID to a wrong value — confirm timeout fires cleanly.
- `13_http_get.py`: switch APIs — try `https://worldtimeapi.org/api/timezone/Etc/UTC` for a smaller payload.
- `14_simple_web_server.py`: add a third route `/status` that returns the LED's current state as JSON.
- `15_mqtt_publish.py`: extend with a subscribe — listen on `tutorial/cmd` and toggle the LED on `"on"` / `"off"` payloads.
