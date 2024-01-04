from ..interface.i2c import I2C  # noqa: F401
from ..interface.uart import UART # noqa: F401
from ..interface.spi import SPI  # noqa: F401
from ..interface.gpio import GPIO# noqa: F401
from ..interface.can import CAN# noqa: F401
from ..interface.ssh import SSH# noqa: F401
from ..controllers.base_controller import BaseController# noqa: F401
from ..utils.parsers.cfg_json_parser import *  # noqa: F403
from ..factory.controllers_inverted_factory import InvertedControllerFactory
from ctypes import *  # noqa: F403
import asyncio
from typing import Any
from concurrent.futures import Future
from threading import Thread


class AsyncLoopThread(Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.loop = asyncio.new_event_loop()

    def run(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()


class TesterManager:  # noqa: F405
    """
    Menager przekazujacy zlecenia do odpowiednich kontrollerow.
    """

    def __init__(self) -> None:
        self.dut = {}
        self.event_loop = AsyncLoopThread()
        self.event_loop.start()

    def _run_coroutine_threadsafe(self, method, *args):
        return asyncio.run_coroutine_threadsafe(method(*args), self.event_loop.loop)

    def _get_controller(self, device: str):
        try:
            return self.dut[device]["controller"]
        except KeyError as e:
            print(f"No controller found for device {device}: {e}")
            return None

    def _generic_controller_method(
        self, device: str, method_name: str, *args
    ) -> Future[Any]:
        controller = self._get_controller(device)
        if controller:
            method = getattr(controller, method_name, None)
            if method:
                return self._run_coroutine_threadsafe(
                    method, self.dut[device]["settings"], *args
                )
            else:
                print(
                    f"Method {method_name} not found in controller for device {device}"
                )
        return asyncio.Future()

    def _grouped_controller_method(
        self, devices: [str], method_name: str, *args
    ) -> Future[Any]:
        controller = self._get_controller(devices[0])
        if controller:
            method = getattr(controller, method_name, None)
            if method:
                try:
                    settings = [self.dut[device]["settings"] for device in devices]
                    return self._run_coroutine_threadsafe(method, settings, *args)
                except KeyError as e:
                    error = asyncio.Future()
                    error.set_result(e)
                    return error
            else:
                print(
                    f"Method {method_name} not found in controller for device {devices[0]}"
                )
        return asyncio.Future()

    def set_config(self, dut: {}):
        self.dut = InvertedControllerFactory.generate_controllers_from_cfg(dut)

    def write_can(self, device: str, data: [int]) -> Future[Any]:
        return self._generic_controller_method(device, "write_can", data)

    def read_can(self, device: str) -> Future[Any]:
        return self._generic_controller_method(device, "read_can")

    def write_i2c(
        self, device: str, data: [int], address: int = 0x1D
    ) -> Future[Any]:
        return self._generic_controller_method(device, "write_i2c", data, address)

    def read_i2c(self, device: str, size:int,address: int = 0x1D) -> Future[Any]:
        return self._generic_controller_method(device, "read_i2c",size, address)

    def spy_i2c(self, device: str, nTransactions: int) -> Future[Any]:
        return self._generic_controller_method(device, "spy_i2c", nTransactions)

    def write_uart(self, device: str, data: [int]) -> Future[Any]:
        return self._generic_controller_method(device, "write_uart", data)

    def read_uart(self, device: str, size: int,time:int) -> Future[Any]:
        return self._generic_controller_method(device, "read_uart",size,time)

    def write_spi(self, device: str, size: int, data: [int]) -> Future[Any]:
        return self._generic_controller_method(device, "write_spi", size, data)

    def read_spi(self, device: str, size: int) -> Future:
        return self._generic_controller_method(device, "read_spi", size)

    def spy_spi(self, device: str, nsamples: int = 30000) -> Future[Any]:
        return self._generic_controller_method(device, "spy_spi", nsamples)

    def write_gpio(self, device: str) -> Future[Any]:
        return self._generic_controller_method(device, "write_gpio")

    def read_gpio(self, device: str) -> Future[Any]:
        return self._generic_controller_method(device, "read_gpio")

    def record_gpio(
        self,
        gpios: [str],
        period_ms: int = 500,
        sample_rate: int = 1000000,
        rising_edge: [int] = None,
        falling_edge: [int] = None,
    ) -> Future[Any]:
        return self._grouped_controller_method(
            gpios, "record_gpio", period_ms, sample_rate, rising_edge, falling_edge
        )

    def send_command(self, device: str, command: str) -> Future[bool]:
        return self._generic_controller_method(device, "send_command", command)
