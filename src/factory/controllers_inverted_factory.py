
from typing import Dict
from src.interface.base_interface import Settings, Interfaces
from src.controllers.base_controller import BaseController


# from ..interface import *
print(Settings.__subclasses__())


# BaseController.__sub
class InvertedControllerFactory:
    """
    Laczy controller parser i plik cfg -> dla zdefiniowanych magistrali i gpios na ducie inicjalizuje odpowiednie sterowniki.
    """

    @staticmethod
    def generate_controllers_from_cfg(cfg: type[Dict]) -> {}:
        dut_dict: Dict[str, dict] = {}
        for controller in cfg:
            try:
                controller_instance = next(
                    instance
                    for instance in BaseController.__subclasses__()
                    if instance.__name__ == controller["controller"]
                )()
            except StopIteration:
                raise Exception(
                    f'controller {controller["controller"]} not defined in ./controllers'
                )
            except KeyError:
                raise Exception(f"check cfg file, no controller field defined")
            for device in controller["devices"]:
                try:
                    settings_dataclass = next(
                        interface
                        for interface in Settings.__subclasses__()
                        if Interfaces(controller["devices"][device]["type"])
                        == interface.eInterface
                    )(**controller["devices"][device]["settings"])
                except ValueError:
                    print(
                        f'interfejs zdefiniowany w configu jako:{controller["devices"][device]["type"]} nie jest obslugiwany przez ten tester'
                    )
                try:
                    dut_dict[device] = {
                        "controller": controller_instance,
                        "settings": settings_dataclass,
                    }
                except ValueError:
                    pass
        return dut_dict


# def _match_settings_to_dataclass(dict_of_interfaces:dict,settings:dict) -> Settings:
#     dataclass_name:str =(settings["type"]+'Settings')
#     if dataclass_name in dict_of_interfaces:
#         return dict_of_interfaces[dataclass_name](**settings["settings"])
