# Minimal ST7789 SPI driver for the Pimoroni Pico Explorer Base (240x240).
# No reset pin (the board ties it to 3v3), so a software reset is used.
# Callers own the framebuf; this driver only blits it to the panel.
#
# Typical use:
#     from machine import SPI, Pin
#     import framebuf
#     from lib import st7789
#     from lib.pins import (
#         ST7789_SPI_ID, ST7789_SCK, ST7789_MOSI,
#         ST7789_CS, ST7789_DC, ST7789_BL,
#         ST7789_WIDTH, ST7789_HEIGHT,
#     )
#
#     spi = SPI(ST7789_SPI_ID, baudrate=31_250_000, polarity=0, phase=0,
#               sck=Pin(ST7789_SCK), mosi=Pin(ST7789_MOSI))
#     lcd = st7789.ST7789(spi, cs=ST7789_CS, dc=ST7789_DC, bl=ST7789_BL,
#                         width=ST7789_WIDTH, height=ST7789_HEIGHT)
#     buf = bytearray(ST7789_WIDTH * ST7789_HEIGHT * 2)
#     fb = framebuf.FrameBuffer(buf, ST7789_WIDTH, ST7789_HEIGHT, framebuf.RGB565)
#     fb.fill(0)
#     fb.text("hello", 10, 10, 0xFFFF)
#     lcd.show(buf)

import time
from machine import Pin, PWM

# ST7789 command set (only the ones we use).
_SWRESET = const(0x01)
_SLPOUT  = const(0x11)
_NORON   = const(0x13)
_INVON   = const(0x21)
_DISPON  = const(0x29)
_CASET   = const(0x2A)
_RASET   = const(0x2B)
_RAMWR   = const(0x2C)
_MADCTL  = const(0x36)
_COLMOD  = const(0x3A)


def color565(r, g, b):
    """Pack 8-8-8 RGB into a 16-bit RGB565 word, byte-swapped for the panel."""
    v = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
    # The ST7789 expects big-endian; framebuf.RGB565 writes little-endian.
    # Swap so fill_rect(..., color565(r, g, b)) renders correctly.
    return ((v & 0xFF) << 8) | (v >> 8)


class ST7789:
    def __init__(self, spi, cs, dc, bl, width=240, height=240, rotation=0):
        self.spi = spi
        self.cs = Pin(cs, Pin.OUT, value=1)
        self.dc = Pin(dc, Pin.OUT, value=0)
        self.bl = PWM(Pin(bl))
        self.bl.freq(1000)
        self.bl.duty_u16(0)
        self.width = width
        self.height = height
        self.rotation = rotation & 0x03
        self._init_panel()

    def _write_cmd(self, cmd):
        self.cs(0)
        self.dc(0)
        self.spi.write(bytes([cmd]))
        self.cs(1)

    def _write_data(self, data):
        self.cs(0)
        self.dc(1)
        self.spi.write(data if isinstance(data, (bytes, bytearray, memoryview))
                       else bytes([data]))
        self.cs(1)

    def _init_panel(self):
        self._write_cmd(_SWRESET)
        time.sleep_ms(150)
        self._write_cmd(_SLPOUT)
        time.sleep_ms(120)
        self._write_cmd(_COLMOD)
        self._write_data(0x55)              # 16 bits/pixel (RGB565)
        self._set_rotation(self.rotation)
        self._write_cmd(_INVON)             # ST7789 needs inversion ON for normal colors
        self._write_cmd(_NORON)
        time.sleep_ms(10)
        self._write_cmd(_DISPON)
        time.sleep_ms(100)

    def _set_rotation(self, r):
        # MADCTL bits: MY=0x80 MX=0x40 MV=0x20 ML=0x10 RGB=0x00 (BGR=0x08).
        # The Pico Explorer Base panel reports colors in RGB order without the BGR bit.
        madctl = (0x00, 0x60, 0xC0, 0xA0)[r & 0x03]
        self._write_cmd(_MADCTL)
        self._write_data(madctl)
        self.rotation = r & 0x03
        if self.rotation & 0x01:
            self.width, self.height = self.height, self.width

    def _set_window(self, x0, y0, x1, y1):
        self._write_cmd(_CASET)
        self._write_data(bytes([x0 >> 8, x0 & 0xFF, x1 >> 8, x1 & 0xFF]))
        self._write_cmd(_RASET)
        self._write_data(bytes([y0 >> 8, y0 & 0xFF, y1 >> 8, y1 & 0xFF]))
        self._write_cmd(_RAMWR)

    def show(self, buf, x=0, y=0, w=None, h=None):
        """Blit a RGB565 framebuf to the panel. Defaults to the full screen."""
        if w is None:
            w = self.width
        if h is None:
            h = self.height
        self._set_window(x, y, x + w - 1, y + h - 1)
        self.cs(0)
        self.dc(1)
        self.spi.write(buf)
        self.cs(1)

    def fill(self, color):
        """Solid color fill via streaming SPI — no big framebuf needed.

        `color` uses the same byte-swapped encoding as color565() so the
        same value works whether you pass it here or to a framebuf method.
        """
        self._set_window(0, 0, self.width - 1, self.height - 1)
        line = bytes([color & 0xFF, color >> 8]) * self.width
        self.cs(0)
        self.dc(1)
        for _ in range(self.height):
            self.spi.write(line)
        self.cs(1)

    def set_backlight(self, duty_u16):
        """0..65535 PWM duty on the BL pin. 0 = off, 65535 = full."""
        self.bl.duty_u16(max(0, min(65535, duty_u16)))
