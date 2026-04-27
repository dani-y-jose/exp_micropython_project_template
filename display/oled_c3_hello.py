# Hello-world for the 0.42" 72x40 OLED on ESP32-C3 dev boards.
# The panel uses an SSD1306 controller but only exposes 72x40 pixels offset
# inside its 128x64 RAM, so show() has to set an explicit column window.
#
# Pins below match the common ESP32-C3 0.42" OLED dev board. Verify against
# your board's silkscreen / schematic if nothing renders.
#
# Install the driver on the board once:
#     uvx mpremote mip install ssd1306

import time
from machine import I2C, Pin
from ssd1306 import SSD1306_I2C

WIDTH = 72
HEIGHT = 40
X_OFFSET = 30  # 72x40 panel is centered inside the SSD1306's 128-pixel row


class OLED72x40(SSD1306_I2C):
    def show(self):
        self.write_cmd(0x21)  # set column address
        self.write_cmd(X_OFFSET)
        self.write_cmd(X_OFFSET + self.width - 1)
        self.write_cmd(0x22)  # set page address
        self.write_cmd(0)
        self.write_cmd(self.pages - 1)
        self.write_data(self.buffer)


i2c = I2C(0, sda=Pin(5), scl=Pin(6), freq=400_000)
oled = OLED72x40(WIDTH, HEIGHT, i2c)

counter = 0
while True:
    oled.fill(0)
    oled.text("TE AMO", 0, 0)
    oled.text("MI DANI", 0, 10)
    oled.text("count: " + str(counter), 0, 25)
    oled.show()
    counter += 1
    time.sleep(0.5)
