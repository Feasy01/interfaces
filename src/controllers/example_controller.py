from ..interface.can import CAN
from ..interface.i2c import I2C
from ..interface.spi import SPI
from ..interface.uart import UART

class ExampleController(CAN,I2C,SPI,UART):
    def __init__(self) -> None:
        pass
 
    def read_can(self) ->(bool, bytes):
        pass
        return (True,b'returned value')


    def write_can(self)->bool:
        pass


    def read_i2c()->(bool, bytes):
        pass
        return (True,b'returned value')


    def write_i2c()->bool:
        pass

    def read_spi(self)->(bool, bytes):
        pass
        return (True,b'returned value')


    def write_spi(self)->bool:
        pass

    def read_uart(self)->(bool, bytes):
        pass
        return (True,b'returned value')

    def write_uart(self)->bool:
        pass

