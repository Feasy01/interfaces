from abc import ABC, abstractmethod
from dataclasses import dataclass
from src.interface.base_interface import Interfaces, Settings

@dataclass
class CANSettings(Settings):
    type:Interfaces.CAN
    tx:int
    rx:int
    frequency:int = 1000000

class CAN(ABC):
    @abstractmethod
    def read_can(self) -> (bool, bytearray):
        pass
    @abstractmethod
    def write_can(self) -> bool:
        pass
