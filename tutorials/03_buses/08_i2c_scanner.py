from machine import I2C, Pin

from lib.pins import I2C_ID, I2C_SCL, I2C_SDA

i2c = I2C(I2C_ID, scl=Pin(I2C_SCL), sda=Pin(I2C_SDA), freq=400_000)

devices = i2c.scan()

if not devices:
    print("no I2C devices found — check wiring and pull-ups")
else:
    print("found", len(devices), "device(s):")
    for addr in devices:
        print("  0x{:02X}".format(addr))
