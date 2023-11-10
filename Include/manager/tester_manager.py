import os
from ..interface.magistrale.spi import SPI
from ..interface.magistrale.i2c import *
from ..interface.magistrale.uart import *
from ..interface.magistrale.spi import *
from ..interface.magistrale.gpio import *
from ..config.CfgParserJson import *
from ..factory.tester_serializer import ControllerFactory
class TesterManager:
    def __init__(self,cfg :os.PathLike) -> None:
        self._dut = ControllerFactory.generate_controllers_from_cfg(cfg)
        pass
    
    def write_can(self,device:str):
        self._dut[str].write_can(str)
    def read_can(self,device:str):
        self._dut[str].read_can(str)
    def write_i2c(self,device:str):
        self._dut[str].write_i2c(str)

    def read_i2c(self, device:str):
        self._dut[str].read_i2c(str)

    def write_uart(self, device:str):
        self._dut[str].wriete_uart(str)

    def read_uart(self ,device:str):
        self._dut[str].read_uart(str)

    def write_spi(self,device:str) -> (bool):
        self._dut[str].write_spi(str)
    def read_spi(self,device:str):
        self._dut[str].read_spi(str)
        
    def write_gpio(self, device:str):
        self._dut[str].write_gpio(str)
        pass
    def read_gpio(self,device:str):
        self._dut[str].read_can(str)
