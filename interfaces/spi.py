from abc import ABC, abstractmethod

class Spi(ABC):
    @abstractmethod
    def read_spi(self):
        pass
    @abstractmethod
    def write_spi(self):
        pass
