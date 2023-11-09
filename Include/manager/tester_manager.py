import os
from ..interfaces.magistrale.can import *
from ..interfaces.magistrale.i2c import *
from ..interfaces.magistrale.uart import *
from ..interfaces.magistrale.spi import *
from ..interfaces.magistrale.gpio import *
from ..config.CfgParserJson import *
from ..factory.tester_serializer import ControllerFactory
class TesterManager:
    def __init__(self,cfg :os.PathLike) -> None:
        self._controllerFactory = ControllerFactory(CfgParserJson.parse_cfg(cfg))
        self._dut = self._controllerFactory.generate_dut()
        pass
    

    def write_can(self,controller:CAN,device:str):
        pass
    def read_can(self,controller:CAN ,device:str):
        pass
    def write_i2c(self,controller:I2C,device:str):
        pass
    def read_i2c(self,controller:I2C, device:str):
        pass
    def write_uart(self,controller:UART, device:str):
        pass
    def read_uart(self,controller:UART ,device:str):
        pass
    def write_spi(self,controller : SPI,device:str) -> (bool):
        controller.spi_write()
        pass
    def read_spi(self,controller:SPI,device:str):
        pass
    def write_gpio(self,controller:GPIO, device:str):
        pass
    def read_gpio(self,controller:GPIO,device:str):
        pass