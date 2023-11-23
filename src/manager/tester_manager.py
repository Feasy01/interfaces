import os
from ..interface.spi import SPI
from ..interface.i2c import *
from ..interface.uart import *
from ..interface.spi import *
from ..interface.gpio import *
from ..interface.can import CAN
from  ..utils.parsers.cfg_json_parser import *
from ..factory.controllers_factory import ControllerFactory
from ..factory.controllers_inverted_factory import InvertedControllerFactory
from ctypes import *

class TesterManager(CAN,SPI,I2C,UART):
    """
    Menager przekazujacy zlecenia do odpowiednich kontrollerow.
    """

    def __init__(self,cfg:os.PathLike) -> None:
        self._dut = InvertedControllerFactory.generate_controllers_from_cfg(CfgParserJson.parse_cfg(cfg))
        print(self._dut)
        pass
    
    def write_can(self,device:str,data:(c_ubyte))->None:
        try:
            self._dut[device]["controller"].write_can(device,data)        
        except KeyError as e:
            print(f'{device} does not have a correlating controller, please check your cfg file')
            pass
    
    def read_can(self,device:str)->None:
        try:
            self._dut[device]["controller"].read_can(device)
        except KeyError as e:
            print(f'{device} does not have a correlating controller, please check your cfg file')
            pass
    
    def write_i2c(self,device:str,data,address:c_ubyte = 0x1D):
        try:
            self._dut[device]["controller"].write_i2c(device,data,address)
        except KeyError as e:
            print(f'{device} does not have a correlating controller, please check your cfg file')
            pass
    
    def read_i2c(self,device:str,data,address:c_ubyte = 0x1D):
        try:
            self._dut[device]["controller"].read_i2c(device,data,address)
        except KeyError as e:
            print(f'{device} does not have a correlating controller, please check your cfg file')
            pass
    
    def write_uart(self, device:str):
        try:
            self._dut[device]["controller"].wriete_uart(device)
        except KeyError as e:
            print(f'{device} does not have a correlating controller, please check your cfg file')
            pass
    
    def read_uart(self ,device:str):
        try:
            self._dut[device]["controller"].read_uart(device)
        except KeyError as e:
            print(f'{device} does not have a correlating controller, please check your cfg file')
            pass
    
    def write_spi(self,device:str) -> (bool):
        try:
            self._dut[device]["controller"].write_spi(device)
        except KeyError as e:
            print(f'{device} does not have a correlating controller, please check your cfg file')
            pass
    
    def read_spi(self,device:str,size):
        try:
            self._dut[device]["controller"].read_spi(device,size)  
        except KeyError as e:
            print(f'{device} does not have a correlating controller, please check your cfg file')
            pass
    
    def write_gpio(self, device:str):
        try:
            self._dut[device]["controller"].write_gpio(device)
        except KeyError as e:
            print(f'{device} does not have a correlating controller, please check your cfg file')
            pass
    
    def read_gpio(self,device:str):
        try:
            self._dut[device]["controller"].read_can(device)
        except KeyError as e:
            print(f'{device} does not have a correlating controller, please check your cfg file')
            pass      

