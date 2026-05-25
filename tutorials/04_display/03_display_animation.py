# Bouncing ball with a live FPS readout. Each frame: clear, draw, blit.
# At 240x240 RGB565 the bottleneck is the 115 KB SPI burst in lcd.show() —
# everything else is in the noise.

import time
import framebuf
from machine import SPI, Pin

from lib.pins import (
    ST7789_SPI_ID, ST7789_SCK, ST7789_MOSI, ST7789_CS, ST7789_DC, ST7789_BL,
    ST7789_WIDTH, ST7789_HEIGHT,
)
from lib.st7789 import ST7789, color565

BG = color565(0, 0, 20)
BALL = color565(255, 100, 0)
TEXT = color565(255, 255, 255)
RADIUS = 12

spi = SPI(ST7789_SPI_ID, baudrate=31_250_000, polarity=0, phase=0,
          sck=Pin(ST7789_SCK), mosi=Pin(ST7789_MOSI))
lcd = ST7789(spi, cs=ST7789_CS, dc=ST7789_DC, bl=ST7789_BL,
             width=ST7789_WIDTH, height=ST7789_HEIGHT)
lcd.set_backlight(40000)

buf = bytearray(ST7789_WIDTH * ST7789_HEIGHT * 2)
fb = framebuf.FrameBuffer(buf, ST7789_WIDTH, ST7789_HEIGHT, framebuf.RGB565)

x, y = 60, 60
dx, dy = 3, 2
frames = 0
fps = 0.0
last_ms = time.ticks_ms()

while True:
    fb.fill(BG)
    fb.fill_rect(x - RADIUS, y - RADIUS, RADIUS * 2, RADIUS * 2, BALL)
    fb.text("fps {:4.1f}".format(fps), 8, 8, TEXT)
    lcd.show(buf)

    x += dx
    y += dy
    if x - RADIUS <= 0 or x + RADIUS >= ST7789_WIDTH:
        dx = -dx
    if y - RADIUS <= 0 or y + RADIUS >= ST7789_HEIGHT:
        dy = -dy

    frames += 1
    if frames >= 20:
        now = time.ticks_ms()
        fps = frames * 1000 / time.ticks_diff(now, last_ms)
        frames = 0
        last_ms = now
