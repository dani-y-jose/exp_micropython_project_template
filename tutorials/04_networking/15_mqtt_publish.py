# Publish ADC readings to an MQTT broker every 5 seconds.
#
#     uvx mpremote mip install umqtt.simple

import json
import network
import sys
import time
from machine import ADC, Pin
from umqtt.simple import MQTTClient

from lib.pins import ADC as ADC_PIN
from lib.secrets import (
    WIFI_SSID,
    WIFI_PASSWORD,
    MQTT_BROKER,
    MQTT_PORT,
    MQTT_USER,
    MQTT_PASSWORD,
    MQTT_CLIENT_ID,
)

TOPIC = b"tutorial/sensor"
INTERVAL_S = 5

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
if not wlan.isconnected():
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    deadline = time.time() + 15
    while not wlan.isconnected() and time.time() < deadline:
        time.sleep(0.5)

if not wlan.isconnected():
    raise RuntimeError("WiFi failed")

adc = ADC(Pin(ADC_PIN))
if sys.platform == "esp32":
    adc.atten(ADC.ATTN_11DB)

client = MQTTClient(
    MQTT_CLIENT_ID,
    MQTT_BROKER,
    port=MQTT_PORT,
    user=MQTT_USER or None,
    password=MQTT_PASSWORD or None,
)
client.connect()
print("mqtt connected to", MQTT_BROKER)

while True:
    payload = json.dumps({"ts": time.time(), "value": adc.read_u16()})
    client.publish(TOPIC, payload.encode())
    print("published:", payload)
    time.sleep(INTERVAL_S)
