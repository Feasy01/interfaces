from ..interface.can import CAN
from ..interface.i2c import I2C
from ..interface.spi import SPI, SPISettings
from ..interface.uart import UART
from ..interface.base_interface import Settings
from .base_controller import BaseController
import asyncio
import time


class ExampleController(BaseController, SPI, CAN, I2C, UART):
    def __init__(self) -> None:
        super().__init__()

    def register_device(self, interface_name: str, settings: Settings):
        super().register_device(interface_name, settings)

    def read_can(self) -> (bool, bytes):
        pass
        return (True, b"returned value")

    def write_can(self) -> bool:
        pass

    def read_i2c() -> (bool, bytes):
        pass
        return (True, b"returned value")

    def write_i2c() -> bool:
        pass

    def read_spi(self) -> (bool, bytes):
        pass
        return (True, b"returned value")

    async def spy_spi(self, device, nSamples):
        siema = 1
        print("robie cos robie cos robie cos")
        print("skonczylem cos robic")
        time.sleep(1)

        while True:
            print("im doing something difficult")
            await asyncio.sleep(1)
            siema += 1
            if siema == 10:
                break
        return True

    def spy_i2c(self, device) -> None:
        return super().spy_i2c(device)

    def write_spi(self) -> bool:
        pass

    def read_uart(self) -> (bool, bytes):
        pass
        return (True, b"returned value")

    def write_uart(self) -> bool:
        pass
