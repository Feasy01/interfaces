from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from src.interface.base_interface import Settings, Interfaces,Interface

@dataclass
class I2CSettings(Settings):
    eInterface:Interfaces = field(default=Interfaces.I2C, init = False)
    scl:int
    sda:int
    frequency:int = 100000
class I2C(Interface):
    eInterface:Interfaces=Interfaces.I2C
    @abstractmethod
    def read_i2c(self) -> (bool, bytearray):
        pass
    @abstractmethod
    def write_i2c(self) -> bool:
        pass
    @abstractmethod
    def spy_i2c(self,device) -> None:
        ...
    def __init_subclass__(cls, **kwargs):
        cls.eInterface = cls.eInterface | I2C.eInterface
        super().__init_subclass__(**kwargs)