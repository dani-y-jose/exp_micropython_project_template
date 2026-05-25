# Drawing primitives via framebuf: pixels, lines, rects, text.
# Everything happens in RAM, then one show() blits the whole buffer to the LCD.

import framebuf
from machine import SPI, Pin

from lib.pins import (
    ST7789_SPI_ID, ST7789_SCK, ST7789_MOSI, ST7789_CS, ST7789_DC, ST7789_BL,
    ST7789_WIDTH, ST7789_HEIGHT,
)
from lib.st7789 import ST7789, color565

WHITE = color565(255, 255, 255)
RED = color565(255, 0, 0)
GREEN = color565(0, 255, 0)
BLUE = color565(0, 0, 255)
YELLOW = color565(255, 220, 0)
GREY = color565(60, 60, 70)
BG = color565(10, 10, 20)

spi = SPI(ST7789_SPI_ID, baudrate=31_250_000, polarity=0, phase=0,
          sck=Pin(ST7789_SCK), mosi=Pin(ST7789_MOSI))
lcd = ST7789(spi, cs=ST7789_CS, dc=ST7789_DC, bl=ST7789_BL,
             width=ST7789_WIDTH, height=ST7789_HEIGHT)
lcd.set_backlight(40000)

buf = bytearray(ST7789_WIDTH * ST7789_HEIGHT * 2)
fb = framebuf.FrameBuffer(buf, ST7789_WIDTH, ST7789_HEIGHT, framebuf.RGB565)

fb.fill(BG)

# Title
fb.text("primitives", 80, 8, WHITE)
fb.hline(0, 20, ST7789_WIDTH, GREY)

# Lines fanning out from a corner
for i in range(0, ST7789_WIDTH, 12):
    fb.line(0, 28, i, 100, YELLOW)

# Outlined and filled rectangles
fb.rect(10, 120, 60, 40, RED)
fb.fill_rect(80, 120, 60, 40, GREEN)
fb.rect(150, 120, 60, 40, BLUE)
fb.fill_rect(160, 130, 40, 20, WHITE)

# A pixel grid in the bottom-left
for x in range(0, 80, 4):
    for y in range(180, 220, 4):
        fb.pixel(x, y, WHITE)

# Multi-line text on the right
fb.text("framebuf", 130, 184, WHITE)
fb.text(".text() and", 130, 196, GREY)
fb.text(".rect() etc.", 130, 208, GREY)

lcd.show(buf)
