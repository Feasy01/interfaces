# form ..Include.controllers import DigitalDiscoveryMultiplex
import os
import importlib
import inspect
import pathlib
from typing import Dict
from src.interface.base_interface import Settings
from src.controllers.base_controller import BaseController
from ..utils.parsers.controllers_parser import ControllerParser
from ..utils.parsers.supported_interfaces_parser import InterfacesParser
class InvertedControllerFactory:
    """
    Laczy controller parser i plik cfg -> dla zdefiniowanych magistrali i gpios na ducie inicjalizuje odpowiednie sterowniki.
    """

    @staticmethod
    def generate_controllers_from_cfg(cfg)->dict:
        dut_dict:Dict[str,dict] = {}
        available_controllers:Dict[str,BaseController] = ControllerParser.dict_of_controllers()
        avalable_interfaces:dict = InterfacesParser.dict_of_interfaces()
        for controller in cfg:
            try:
                controller_instance = available_controllers[controller["controller"]]()
            except KeyError:
                raise(f'controller not defined in ./controllers')
            for device in controller["devices"]:
                settings_dataclass = _match_settings_to_dataclass(avalable_interfaces,controller["devices"][device])
                controller_instance.register_device(device,settings_dataclass)
                dut_dict[device] = {"controller":controller_instance,
                                    "settings":_match_settings_to_dataclass(avalable_interfaces,controller["devices"][device])}
        return dut_dict


def _match_settings_to_dataclass(dict_of_interfaces:dict,settings:dict) -> Settings:
    dataclass_name:str =(settings["type"]+'Settings')
    if dataclass_name in dict_of_interfaces:
        return dict_of_interfaces[dataclass_name](**settings["settings"])

