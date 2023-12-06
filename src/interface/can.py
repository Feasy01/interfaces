from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from src.interface.base_interface import Interfaces, Settings,Interface

@dataclass
class CANSettings(Settings):
    eInterface:Interfaces = field(default=Interfaces.CAN, init=False)
    tx:int
    rx:int
    frequency:int = 1000000

class CAN(Interface):
    eInterface:Interfaces = Interfaces.CAN
    @abstractmethod
    def read_can(self) -> (bool, bytearray):
        pass
    @abstractmethod
    def write_can(self) -> bool:
        pass

    def __init_subclass__(cls, **kwargs):
        cls.eInterface = cls.eInterface | CAN.eInterface
        super().__init_subclass__(**kwargs)