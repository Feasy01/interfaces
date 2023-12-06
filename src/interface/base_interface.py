from dataclasses import dataclass
from enum import Enum
from abc import abstractmethod, ABC


class Interfaces(Enum):
    CAN = "CAN"
    GPIO = "GPIO"
    I2C = "I2C"
    QSPI = "QSPI"
    SPI = "SPI"
    UART = "UART"
    SSH = "SSH"

    def __or__(self, other):
        if isinstance(other, set):
            return {self} | other
        elif isinstance(other, Interfaces):
            return {self, other}
        elif other is None:
            return {self}
        else:
            raise TypeError

    def __ror__(self, other):
        if isinstance(other, set):
            return other | {self}
        elif isinstance(other, Interfaces):
            return {other, self}
        elif other is None:
            return {self}
        else:
            raise TypeError


@dataclass
class Settings:
    eInterface: Interfaces


class Interface(ABC):
    @abstractmethod
    def __init_subclass__(cls, **kwargs):
        ...

    @property
    @abstractmethod
    def eInterface():
        ...



