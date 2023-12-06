from dataclasses import dataclass, field
from src.interface.base_interface import Settings, Interfaces, Interface


@dataclass
class QSPISettings(Settings):
    eInterface: Interfaces = field(default=Interfaces.QSPI, init=False)
    dq0: int
    dq1: int
    dq2: int
    da3: int
    clk: int
    cs: int
    frequency: int = 100000


class QSPI(Interface):
    eInterface: Interfaces = Interfaces.QSPI

    def read_qspi(self) -> None:
        ...

    def write_qspi(self) -> None:
        ...

    def __init_subclass__(cls, **kwargs):
        cls.eInterface = cls.eInterface | QSPI.eInterface
        super().__init_subclass__(**kwargs)
