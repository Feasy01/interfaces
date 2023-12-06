from abc import abstractmethod
from dataclasses import dataclass, field
from src.interface.base_interface import Interfaces, Settings, Interface


@dataclass
class GPIOSettings(Settings):
    eInterface: Interfaces = field(default=Interfaces.GPIO, init=False)
    pin: int
    default: int


class GPIO(Interface):
    eInterface: Interfaces = Interfaces.GPIO

    @abstractmethod
    def read_gpio(self, pin) -> (bool, bytes):
        pass

    @abstractmethod
    def record_gpio(
        self,
        pins: [GPIOSettings],
        period_ms: int,
        rising_edge: str = None,
        falling_edge: str = None,
    ) -> (bool, bytearray):
        ...

    def __init_subclass__(cls, **kwargs):
        cls.eInterface = cls.eInterface | GPIO.eInterface
        super().__init_subclass__(**kwargs)
