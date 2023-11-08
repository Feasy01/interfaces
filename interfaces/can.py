from abc import ABC, abstractmethod

class Can(ABC):
    @abstractmethod
    def read_can(self) -> (bool, bytearray):
        pass
    @abstractmethod
    def write_can(self) -> bool:
        pass
