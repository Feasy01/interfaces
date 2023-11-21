from abc import ABC, abstractmethod

class UART(ABC):
    @abstractmethod
    def read_uart(self):
        pass
    @abstractmethod
    def write_uart(self):
        pass
