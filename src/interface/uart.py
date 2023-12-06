from abc import abstractmethod
from dataclasses import dataclass, field
from src.interface.base_interface import Settings, Interfaces, Interface


@dataclass
class UARTSettings(Settings):
    eInterface: Interfaces = field(default=Interfaces.UART, init=False)
    tx: int
    rx: int
    frequency: int = 100000


class UART(Interface):
    eInterface: Interfaces = Interfaces.UART

    @abstractmethod
    def read_uart(self, device: str, data: bytes):
        pass

    @abstractmethod
    def write_uart(self, device: str, data: bytes):
        pass

    def __init_subclass__(cls, **kwargs):
        cls.eInterface = cls.eInterface | UART.eInterface
        super().__init_subclass__(**kwargs)
