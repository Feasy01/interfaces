from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class SPIConfig:
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