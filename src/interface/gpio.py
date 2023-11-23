from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from src.interface.base_interface import Interfaces, Settings
@dataclass
class GPIOSettings(Settings):
    type:Interfaces = field(default=Interfaces.GPIO, init = False)
    pin:int
class GPIO(ABC):
    @abstractmethod
    def read(self,pin) -> (bool,bytes):
        pass
    @abstractmethod
    def sample(self,pin,time_period) -> (bool , bytearray):
        pass