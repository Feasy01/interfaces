from abc import ABC, abstractmethod
from dataclasses import dataclass,field
from src.interface.base_interface import Settings, Interfaces,Interface

@dataclass
class SSHSettings(Settings):
    eInterface:Interfaces = field(init=False, default=Interfaces.SSH)
    hostname:str
    username:str
    password:str
    port:int = field(default=22)


class SSH(Interface):
    eInterface:Interfaces = Interfaces.SSH
    @abstractmethod
    def send_command(self,command:str) -> None:
        ...
    def __init_subclass__(cls, **kwargs):
        cls.eInterface = cls.eInterface | SSH.eInterface
        super().__init_subclass__(**kwargs)