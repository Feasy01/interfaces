from dataclasses import dataclass
from enum import auto, Enum
from abc import abstractmethod, ABC

class Interfaces(Enum):
    CAN = "CAN"
    GPIO = "GPIO"
    I2C = "I2C"
    QSPI = "QSPI"
    SPI = "SPI"
    UART = "UART"


@dataclass
class Settings:
    type: Interfaces

class Interface(ABC):
    @property
    @abstractmethod
    def type(self) -> Interfaces:
        """each interface """


