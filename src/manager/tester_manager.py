import os
from ..interface.spi import SPI
from ..interface.i2c import *
from ..interface.uart import *
from ..interface.spi import *
from ..interface.gpio import *
from ..interface.can import CAN
from ..interface.ssh import SSH
from  ..utils.parsers.cfg_json_parser import *
from ..factory.controllers_factory import ControllerFactory
from ..factory.controllers_inverted_factory import InvertedControllerFactory
from ctypes import *
import asyncio
from typing import Any
from concurrent.futures import Future
from threading import Thread



class AsyncLoopThread(Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.loop = asyncio.new_event_loop()

    def run(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

# from types import Awaitable
class TesterManager(CAN,SPI,I2C,UART,SSH):
    """
    Menager przekazujacy zlecenia do odpowiednich kontrollerow.
    """

    def __init__(self,cfg:os.PathLike) -> None:
        self._dut = InvertedControllerFactory.generate_controllers_from_cfg(CfgParserJson.parse_cfg(cfg))
        self.event_loop = AsyncLoopThread()
        self.event_loop.start()
        pass
    
    async def write_can(self,device:str,data:(c_ubyte))->None:
        try:
           return asyncio.run_coroutine_threadsafe(self._dut[device]["controller"].write_can(device,data),self.event_loop.loop)      
        except NoControllerException(device):
            pass
    
    def read_can(self,device:str)->None:
        try:
            return asyncio.run_coroutine_threadsafe(self._dut[device]["controller"].read_can(device),self.event_loop.loop) 
        except NoControllerException(device):
            pass
    
    def write_i2c(self,device:str,data,address:c_ubyte = 0x1D):
        try:
            return asyncio.run_coroutine_threadsafe(self._dut[device]["controller"].write_i2c(device,data,address),self.event_loop.loop) 
        except NoControllerException(device):
            pass
    
    def read_i2c(self,device:str,data,address:c_ubyte = 0x1D):
        try:
            return asyncio.run_coroutine_threadsafe(self._dut[device]["controller"].read_i2c(device,data,address),self.event_loop.loop) 
        except NoControllerException(device):
            pass
    def spy_i2c(self,device:str,data:int):
        try:
            return asyncio.run_coroutine_threadsafe(self._dut[device]["controller"].spy_i2c(device,data),self.event_loop.loop) 
        except NoControllerException(device):
            pass
    def write_uart(self, device:str):
        try:
            return asyncio.run_coroutine_threadsafe(self._dut[device]["controller"].wriete_uart(device),self.event_loop.loop) 
        except NoControllerException(device):
            pass
    
    def read_uart(self ,device:str):
        try:
            return asyncio.run_coroutine_threadsafe(elf._dut[device]["controller"].read_uart(device),self.event_loop.loop)
            return task
        except NoControllerException(device):
            pass
    
    def write_spi(self,device:str) -> (bool):
        try:
            return asyncio.run_coroutine_threadsafe(self._dut[device]["controller"].write_spi(device),self.event_loop.loop)
            return task
        except NoControllerException(device):
            pass
    
    def read_spi(self,device:str,size) -> Future:
        try:
            return asyncio.run_coroutine_threadsafe(self._dut[device]["controller"].read_spi(device,size),self.event_loop.loop)
        except NoControllerException(device):
            pass

    def spy_spi(self,device:str,nsamples:int) -> ...:
        try:
            return asyncio.run_coroutine_threadsafe(self._dut[device]["controller"].spy_spi(device,nsamples),self.event_loop.loop)
        except NoControllerException(device):
            pass
    
    def write_gpio(self, device:str):
        try:
            return asyncio.run_coroutine_threadsafe(self._dut[device]["controller"].write_gpio(device),self.event_loop.loop)
        except NoControllerException(device):
            pass
    
    def read_gpio(self,device:str) -> Future[Any]:
        try:
            return asyncio.run_coroutine_threadsafe(self._dut[device]["controller"].read_can(device),self.event_loop.loop)
        except NoControllerException(device):
            pass     
    def send_command(self,device:str,command:str) -> Future[bool]:
        try:
            return asyncio.run_coroutine_threadsafe(self._dut[device]["controller"].send_command(command),self.event_loop.loop)
        except NoControllerException(device):
            pass


class NoControllerException(KeyError):
    def __init__(self,device, message = "does not have a correlating controller, please check your cfg file'") -> None:
        super().__init__(message=f'{device}{message}')