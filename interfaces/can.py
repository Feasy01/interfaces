from abc import ABC, abstractmethod

class Can(ABC):
    @abstractmethod
    def read_can(self):
        pass
    @abstractmethod
    def write_can(self):
        pass
