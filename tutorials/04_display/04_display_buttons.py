# Read the Pico Explorer Base's four onboard buttons (A/B/X/Y) and render
# their state as four boxes. Buttons are active-low with internal pull-ups.

import time
import framebuf
from machine import SPI, Pin

from lib.pins import (
    ST7789_SPI_ID, ST7789_SCK, ST7789_MOSI, ST7789_CS, ST7789_DC, ST7789_BL,
    ST7789_WIDTH, ST7789_HEIGHT,
    BTN_A, BTN_B, BTN_X, BTN_Y,
)
from lib.st7789 import ST7789, color565

BG = color565(10, 10, 20)
IDLE = color565(40, 40, 60)
ACTIVE = color565(255, 180, 0)
LABEL = color565(255, 255, 255)

spi = SPI(ST7789_SPI_ID, baudrate=31_250_000, polarity=0, phase=0,
          sck=Pin(ST7789_SCK), mosi=Pin(ST7789_MOSI))
lcd = ST7789(spi, cs=ST7789_CS, dc=ST7789_DC, bl=ST7789_BL,
             width=ST7789_WIDTH, height=ST7789_HEIGHT)
lcd.set_backlight(40000)

buttons = (
    ("A", Pin(BTN_A, Pin.IN, Pin.PULL_UP),  20,  50),
    ("B", Pin(BTN_B, Pin.IN, Pin.PULL_UP),  20, 150),
    ("X", Pin(BTN_X, Pin.IN, Pin.PULL_UP), 140,  50),
    ("Y", Pin(BTN_Y, Pin.IN, Pin.PULL_UP), 140, 150),
)

buf = bytearray(ST7789_WIDTH * ST7789_HEIGHT * 2)
fb = framebuf.FrameBuffer(buf, ST7789_WIDTH, ST7789_HEIGHT, framebuf.RGB565)

while True:
    fb.fill(BG)
    fb.text("press a button", 56, 10, LABEL)
    for label, pin, bx, by in buttons:
        pressed = not pin.value()  # active-low
        fb.fill_rect(bx, by, 80, 60, ACTIVE if pressed else IDLE)
        fb.rect(bx, by, 80, 60, LABEL)
        fb.text(label, bx + 36, by + 26, LABEL)
    lcd.show(buf)
    time.sleep_ms(30)
