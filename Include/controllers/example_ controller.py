from ..interfaces.can import Can
from ..interfaces.i2c import I2c
from ..interfaces.spi import Spi
from ..interfaces.uart import Uart
from typing import override

class ExampleController(Can,I2c,Spi,Uart):
    def __init__(self) -> None:
        self._Discovery = 'mock'
        # self._Discovery.someInitialization
    
    @override   
    def read_can(self) ->(bool, bytes):
        pass
        return (True,b'returned value')

    @override
    def write_can(self)->bool:
        pass

    @override
    def read_i2c()->(bool, bytes):
        pass
        return (True,b'returned value')

    @override
    def write_i2c()->bool:
        pass

    @override
    def read_spi(self)->(bool, bytes):
        pass
        return (True,b'returned value')

    @override
    def write_spi(self)->bool:
        pass

    @override
    def read_uart(self)->(bool, bytes):
        pass
        return (True,b'returned value')

    @override
    def write_uart(self)->bool:
        pass

