# Standard 128x64 SSD1306 OLED. For the 0.42" 72x40 panel on ESP32-C3 boards,
# see display/oled_c3_hello.py — that one needs a column-window override.
#
#     uvx mpremote mip install ssd1306

import time
from machine import I2C, Pin
from ssd1306 import SSD1306_I2C

from lib.pins import I2C_ID, I2C_SCL, I2C_SDA

WIDTH = 128
HEIGHT = 64

i2c = I2C(I2C_ID, scl=Pin(I2C_SCL), sda=Pin(I2C_SDA), freq=400_000)
oled = SSD1306_I2C(WIDTH, HEIGHT, i2c)

x = 0
while True:
    oled.fill(0)
    oled.text("MicroPython", 0, 0)
    oled.text("Tutorial 10", 0, 12)
    oled.rect(x, 40, 16, 16, 1)
    oled.show()
    x = (x + 4) % (WIDTH - 16)
    time.sleep_ms(80)
