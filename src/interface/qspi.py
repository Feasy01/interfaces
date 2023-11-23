from abc import abstractmethod,ABC
from dataclasses import dataclass,field
from src.interface.base_interface import Settings, Interfaces

@dataclass
class QSPISettings(Settings):
    type:Interfaces = field(default=Interfaces.QSPI, init = False)
    dq0:int
    dq1:int
    dq2:int
    da3:int
    clk:int
    cs:int
    frequency:int = 100000


class QSPI(ABC):
    def read_qspi(self)->None:
        ...
    def write_qspi(self) ->None:
        ...