from machine import Pin, SPI, PWM, I2C
import time

OLED_SCLK = 10
OLED_MOSI = 11
OLED_DC = 12
OLED_CS = 13
OLED_RST = 14
OLED_PWR = 15

TP_SCL = 7
TP_SDA = 6
TP_RST = 17
TP_INT = 16

class CO5300(object):
    def __init__(self, width, height, rotation = 0, offset_x = 0, offset_y = 0):
        self.spi = SPI(1, 80_000_000, polarity = 0, phase = 0, bits = 8, sck = Pin(OLED_SCLK), mosi = Pin(OLED_MOSI), miso = None)
        self.pwr = Pin(OLED_PWR, Pin.OUT)
        self.cs = Pin(OLED_CS, Pin.OUT)
        self.dc = Pin(OLED_DC, Pin.OUT)
        self.rst = Pin(OLED_RST, Pin.OUT)
        # self.bl = PWM(Pin(LCD_BL))
        # self.bl.freq(5000)
        self.width = width
        self.height = height
        self.rotation = rotation
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.pwr(1)
        self.reset()
        self.config()
    
    def write_cmd(self, cmd):
        self.cs(0)
        self.dc(0)
        self.spi.write(bytearray([cmd]))
        self.cs(1)
    
    def write_data(self, data):
        self.cs(0)
        self.dc(1)
        self.spi.write(bytearray([data]))
        self.cs(1)
    def set_brightness(self, brightness):
        self.write_cmd(0x51)
        self.write_data(brightness)
    def reset(self):
        self.rst(1)
        time.sleep(0.01)
        self.rst(0)
        time.sleep(0.01)
        self.rst(1)
    def set_windows(self, x0, y0, x1, y1):
        x0 = x0 + self.offset_x
        y0 = y0 + self.offset_y
        x1 = x1 + self.offset_x
        y1 = y1 + self.offset_y
        
        self.write_cmd(0x2a)
        self.write_data(x0 >> 8)
        self.write_data(x0 & 0xff)
        self.write_data(x1 >> 8)
        self.write_data(x1 & 0xff)
        self.write_cmd(0x2b)
        self.write_data(y0 >> 8)
        self.write_data(y0 & 0xff)
        self.write_data(y1 >> 8)
        self.write_data(y1 & 0xff)
        self.write_cmd(0x2c)
    def flush(self, color):
        self.dc(1)
        self.cs(0)
        self.spi.write(color)
        self.cs(1)
    def config(self):
        self.write_cmd(0x11)
        
        self.write_cmd(0xc4)
        self.write_data(0x80)
        
        self.write_cmd(0x44)
        self.write_data(0x01)
        self.write_data(0xD7)
        
        self.write_cmd(0x35)
        self.write_data(0x00)
        
        self.write_cmd(0x53)
        self.write_data(0x20)
        
        self.write_cmd(0x29)
        
        self.write_cmd(0x51)
        self.write_data(0xA0)
        
        self.write_cmd(0x20)
        
        self.write_cmd(0x36)
        self.write_data(0x00)
        
        self.write_cmd(0x3A)
        self.write_data(0x05)
        time.sleep(0.12)


class FT6146(object):
    def __init__(self, i2c, width, height, device_addr = 0x38, rotation = 0, offset_x = 0, offset_y = 0):
        self.i2c = i2c
        self.width = width
        self.height = height
        self.device_addr = device_addr
        self.rotation = rotation
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.read_flag = False
        self.rst = Pin(TP_RST, Pin.OUT)
        self.int = Pin(TP_INT, Pin.IN, Pin.PULL_UP)
        self.int.irq(handler = self.int_callback, trigger = Pin.IRQ_FALLING)
        self.coords = [{"x": 0, "y": 0} for _ in range(2)]
        self.points = 0
        self.reset()
        id = self.read_id()
        if id :
            print("FT6146 is OK!")
        else:
            print("FT6146 is not OK!")
    
    def int_callback(self, pin):
        self.read_flag = True
    def reset(self):
        self.rst(1)
        time.sleep(0.01)
        self.rst(0)
        time.sleep(0.01)
        self.rst(1)
        time.sleep(0.1)
    def write(self, buf):
        buf_high = (buf >> 8) & 0xFF
        buf_low = buf & 0xFF
        self.i2c.writeto_mem(self.device_addr, buf_high, bytes([buf_low]), addrsize = 8)
        
    def write_reg(self, reg, value):
        self.i2c.writeto_mem(self.device_addr, reg, value, addrsize = 8)
    
    def read_reg(self, reg, len):
        data = self.i2c.readfrom_mem(self.device_addr, reg, len, addrsize = 8)
        return data

    def read_id(self):
        FT6146_REG_ID = 0xA0
        buf = bytearray(1)
        buf = self.read_reg(FT6146_REG_ID, 1)
        if (buf[0] != 0x03):
            return False
        return True
        
    def get_coords(self):
        if self.points == 0:
            return None
        else:
            coords = [{"x": self.coords[i]["x"], "y": self.coords[i]["y"]} for i in range(self.points)]
            return coords
        
    def read_touch(self):
        self.points = 0
        if self.read_flag == False:
            return False
        FT6146_REG_STATUS = 0x02
        
        
        buf = bytearray(11)
        buf = self.read_reg(FT6146_REG_STATUS, 11)
        
        if ((buf[0] & 0x0F) == 0x00):
            return False
        self.points = buf[0] & 0x0F;
        for i in range(self.points):
            self.coords[i]["x"] = ((buf[1 + 6 * i] & 0x0f) << 8)  + buf[2 + 6 * i]
            self.coords[i]["y"] = ((buf[3 + 6 * i] & 0x0f) << 8) +  buf[4 + 6 * i]
        return True
            
