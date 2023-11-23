from abc import ABC, abstractmethod
from dataclasses import dataclass,field
from src.interface.base_interface import Settings, Interfaces


@dataclass
class UARTSettings(Settings):
    type:Interfaces = field(default=Interfaces.UART, init = False)
    tx:int
    rx:int
    frequency:int = 100000
class UART(ABC):
    @abstractmethod
    def read_uart(self):
        pass
    @abstractmethod
    def write_uart(self):
        pass
