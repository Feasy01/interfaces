from abc import abstractmethod
from dataclasses import dataclass, field
from src.interface.base_interface import Settings, Interfaces, Interface


@dataclass
class SPISettings(Settings):
    eInterface: Interfaces = field(default=Interfaces.SPI, init=False)
    clk: int = field(default=None)
    miso: int = field(default=None)
    mosi: int = field(default=None)
    cs: int = field(default=None)
    frequency: int = field(default=2_500_000)


class SPI(Interface):
    eInterface: Interfaces = Interfaces.SPI

    @abstractmethod
    def read_spi(self) -> (bool, bytearray):
        ...

    @abstractmethod
    def write_spi(self):
        ...

    @abstractmethod
    def spy_spi(self, device: str):
        ...

    def __init_subclass__(cls, **kwargs):
        cls.eInterface = cls.eInterface | SPI.eInterface
        super().__init_subclass__(**kwargs)
