from src.interface.base_interface import Settings, Interfaces


class BaseController:
    eInterface: Interfaces

    def __init__(self):
        self.settings: dict = {}

    def __str__(self) -> str:
        return f"{self.__class__.__name__}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}"

    def register_device(self, interface_name: str, settings: Settings):
        if settings.eInterface in self.eInterface:
            pass
        else:
            raise ValueError(f"{interface_name} can not be handled by {self.__name__}")

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
