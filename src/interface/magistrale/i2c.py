from abc import ABC, abstractmethod

class I2C(ABC):
    @abstractmethod
    def read_i2c(self) -> (bool, bytearray):
        pass
    @abstractmethod
    def write_i2c(self) -> bool:
        pass
