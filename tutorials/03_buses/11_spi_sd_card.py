# Mounts an SD card over SPI, writes a line, reads it back, then unmounts.
#
#     uvx mpremote mip install sdcard

import os
import sdcard
from machine import SPI, Pin

from lib.pins import SPI_ID, SPI_SCK, SPI_MOSI, SPI_MISO, SPI_CS

spi = SPI(
    SPI_ID,
    baudrate=1_000_000,
    sck=Pin(SPI_SCK),
    mosi=Pin(SPI_MOSI),
    miso=Pin(SPI_MISO),
)
cs = Pin(SPI_CS, Pin.OUT)

sd = sdcard.SDCard(spi, cs)
os.mount(sd, "/sd")

print("mounted. contents of /sd:", os.listdir("/sd"))

with open("/sd/hello.txt", "w") as f:
    f.write("hello from MicroPython tutorial 11\n")

with open("/sd/hello.txt", "r") as f:
    print("read back:", f.read().strip())

os.umount("/sd")
print("unmounted")
