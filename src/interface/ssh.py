from abc import ABC, abstractmethod
from dataclasses import dataclass,field
from src.interface.base_interface import Settings, Interfaces

@dataclass
class SSHSettings(Settings):
    type:Interfaces = field(init=False, default=Interfaces.SSH)
    hostname:str
    username:str
    password:str
    port:int = field(default=22)


class SSH(ABC):
    @abstractmethod
    def send_command(self,command:str) -> None:
        ...
    