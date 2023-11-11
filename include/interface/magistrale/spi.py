from abc import ABC, abstractmethod

class SPI(ABC):
    @abstractmethod
    def read_spi(self) -> (bool, bytearray):
        pass
    @abstractmethod
    def write_spi(self):
        pass
