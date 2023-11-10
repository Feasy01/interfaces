from ..interface.magistrale.can import CAN
from ..interface.magistrale.i2c import I2C
from ..interface.magistrale.spi import SPI
from ..interface.magistrale.uart import UART

class ExampleController(CAN,I2C,SPI,UART):
    def __init__(self) -> None:
        self._Discovery = 'mock'
        # self._Discovery.someInitialization
    
 
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

