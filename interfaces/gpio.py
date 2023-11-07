from abc import ABC, abstractmethod


class Gpio(ABC):
    def read(self,pin) -> (bool,bytes):
        pass
    def sample(self,pin,time_period) -> (bool , bytearray):
        pass