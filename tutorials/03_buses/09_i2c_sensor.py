# DHT22 actually uses a 1-wire protocol, not I2C — but the pattern of "import a
# driver, hand it a Pin, call read methods" is exactly the same as a real I2C
# sensor. For a true I2C sensor instead, install bme280 and swap the driver:
#     uvx mpremote mip install bme280

import time
import dht
from machine import Pin

from lib.pins import I2C_SDA  # reuse SDA pin as the 1-wire data line

sensor = dht.DHT22(Pin(I2C_SDA))

while True:
    sensor.measure()
    print("temp:", sensor.temperature(), "C  humidity:", sensor.humidity(), "%")
    time.sleep(2)
