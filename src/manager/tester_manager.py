import os
from ..interface.magistrale.spi import SPI
from ..interface.magistrale.i2c import *
from ..interface.magistrale.uart import *
from ..interface.magistrale.spi import *
from ..interface.magistrale.gpio import *
from ..interface.magistrale.can import CAN
from  ..utils.parsers.cfg_json_parser import *
from ..factory.controllers_factory import ControllerFactory
from ctypes import *

class TesterManager(CAN,SPI,I2C,UART):
    """
    Menager przekazujacy zlecenia do odpowiednich kontrollerow.
    """

    def __init__(self,cfg:os.PathLike) -> None:
        self._dut = ControllerFactory.generate_controllers_from_cfg(CfgParserJson.parse_cfg(cfg))
        pass
    
    def write_can(self,device:str,data:(c_ubyte))->None:
        try:
            self._dut[device].write_can(device,data)        
        except KeyError as e:
            print(f'{device} does not have a correlating controller, please check your cfg file')
            pass
    
    def read_can(self,device:str)->None:
        try:
            self._dut[device].read_can(device)
        except KeyError as e:
            print(f'{device} does not have a correlating controller, please check your cfg file')
            pass
    
    def write_i2c(self,device:str,data,address:c_ubyte = 0x1D):
        try:
            self._dut[device].write_i2c(device,data,address)
        except KeyError as e:
            print(f'{device} does not have a correlating controller, please check your cfg file')
            pass
    
    def read_i2c(self,device:str,data,address:c_ubyte = 0x1D):
        try:
            self._dut[device].read_i2c(device,data,address)
        except KeyError as e:
            print(f'{device} does not have a correlating controller, please check your cfg file')
            pass
    
    def write_uart(self, device:str):
        try:
            self._dut[device].wriete_uart(device)
        except KeyError as e:
            print(f'{device} does not have a correlating controller, please check your cfg file')
            pass
    
    def read_uart(self ,device:str):
        try:
            self._dut[device].read_uart(device)
        except KeyError as e:
            print(f'{device} does not have a correlating controller, please check your cfg file')
            pass
    
    def write_spi(self,device:str) -> (bool):
        try:
            self._dut[device].write_spi(device)
        except KeyError as e:
            print(f'{device} does not have a correlating controller, please check your cfg file')
            pass
    
    def read_spi(self,device:str):
        try:
            self._dut[device].read_spi(device)  
        except KeyError as e:
            print(f'{device} does not have a correlating controller, please check your cfg file')
            pass
    
    def write_gpio(self, device:str):
        try:
            self._dut[device].write_gpio(device)
        except KeyError as e:
            print(f'{device} does not have a correlating controller, please check your cfg file')
            pass
    
    def read_gpio(self,device:str):
        try:
            self._dut[device].read_can(device)
        except KeyError as e:
            print(f'{device} does not have a correlating controller, please check your cfg file')
            pass      

