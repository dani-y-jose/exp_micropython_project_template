# Pimoroni Pico Explorer Base onboard ST7789 LCD (240x240, SPI0).
# Driver lives at lib/st7789.py — no mip install needed.

import time
import framebuf
from machine import SPI, Pin

from lib.pins import (
    ST7789_SPI_ID, ST7789_SCK, ST7789_MOSI, ST7789_CS, ST7789_DC, ST7789_BL,
    ST7789_WIDTH, ST7789_HEIGHT,
)
from lib.st7789 import ST7789, color565

spi = SPI(ST7789_SPI_ID, baudrate=31_250_000, polarity=0, phase=0,
          sck=Pin(ST7789_SCK), mosi=Pin(ST7789_MOSI))
lcd = ST7789(spi, cs=ST7789_CS, dc=ST7789_DC, bl=ST7789_BL,
             width=ST7789_WIDTH, height=ST7789_HEIGHT)
lcd.set_backlight(40000)

# Quick color sweep using the driver's streaming fill — no framebuf allocated.
for c in (color565(255, 0, 0), color565(0, 255, 0), color565(0, 0, 255),
          color565(255, 255, 255), color565(0, 0, 0)):
    lcd.fill(c)
    time.sleep_ms(400)

# Allocate one full-screen framebuffer (240*240*2 = 115 KB) and draw to it.
buf = bytearray(ST7789_WIDTH * ST7789_HEIGHT * 2)
fb = framebuf.FrameBuffer(buf, ST7789_WIDTH, ST7789_HEIGHT, framebuf.RGB565)
fb.fill(color565(0, 0, 30))
fb.text("hello, world", 76, 116, color565(255, 255, 255))
lcd.show(buf)
