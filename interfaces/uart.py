from abc import ABC, abstractmethod

class Uart(ABC):
    @abstractmethod
    def read_uart(self):
        pass
    @abstractmethod
    def write_uart(self):
        pass
