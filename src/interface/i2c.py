from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from src.interface.base_interface import Settings, Interfaces

@dataclass
class I2CSettings(Settings):
    type:Interfaces = field(default=Interfaces.I2C, init = False)
    scl:int
    sda:int
    frequency:int = 100000
class I2C(ABC):
    @abstractmethod
    def read_i2c(self) -> (bool, bytearray):
        pass
    @abstractmethod
    def write_i2c(self) -> bool:
        pass
