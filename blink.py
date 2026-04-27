import machine
import time

# Adjust to your board's onboard LED (commonly 2 on ESP32 DevKit, 48 on ESP32-S3).
LED_PIN = 2

led = machine.Pin(LED_PIN, machine.Pin.OUT)

while True:
    led.value(1)
    print("on")
    time.sleep(0.5)

    led.value(0)
    print("off")
    time.sleep(0.5)
