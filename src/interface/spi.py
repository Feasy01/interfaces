from abc import ABC, abstractmethod
from dataclasses import dataclass,field
from src.interface.base_interface import Settings, Interfaces

@dataclass
class SPISettings(Settings):
    type:Interfaces = field(default=Interfaces.SPI, init = False)
    clk:int = field(default = None)
    miso:int = field(default = None)
    mosi:int = field(default = None)
    cs:int = field(default = None)
    frequency:int = field(default= 2_500_000)

class SPI(ABC):
    @abstractmethod
    def read_spi(self) -> (bool, bytearray):
        pass
    @abstractmethod
    def write_spi(self):
        pass
    @abstractmethod
    def spy_spi(self,device:str):
        ...
    # @abstractmethod
    # def _configure_spi(self,settings:SPIConfig) -> None:
    #     pass