from abc import ABC, abstractmethod
from dataclasses import dataclass,field
from src.interface.base_interface import Settings, Interfaces

@dataclass
class SPISettings(Settings):
    type:Interfaces = field(default=Interfaces.SPI, init = False)
    clk:int
    miso:int
    mosi:int
    cs:int
    frequency:int

class SPI(ABC):
    @abstractmethod
    def read_spi(self) -> (bool, bytearray):
        pass
    @abstractmethod
    def write_spi(self):
        pass
    
    # @abstractmethod
    # def _configure_spi(self,settings:SPIConfig) -> None:
    #     pass