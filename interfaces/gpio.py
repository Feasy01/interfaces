from abc import ABC, abstractmethod


class Gpio(ABC):
    @abstractmethod
    def read(self,pin) -> (bool,bytes):
        pass
    @abstractmethod
    def sample(self,pin,time_period) -> (bool , bytearray):
        pass