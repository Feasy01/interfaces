# form ..Include.controllers import DigitalDiscoveryMultiplex
import os
import importlib
import inspect
import pathlib
from ..utils.parsers.controllers_parser import ControllerParser
class ControllerFactory:
    """
    Laczy controller parser i plik cfg -> dla zdefiniowanych magistrali i gpios na ducie inicjalizuje odpowiednie sterowniki.
    """

    @staticmethod
    def generate_controllers_from_cfg(cfg)->dict:
        dut_dict:dict = {}
        available_controllers:dict = ControllerParser.dict_of_controllers()
        print(available_controllers)
        for interface in cfg.keys():
            try:
                class_name,instance_vars = cfg[interface].popitem()
                if class_name in available_controllers:
                    controller_instance = available_controllers[class_name].assign_instance(interface,
                                                                                            instance_vars["id"],
                                                                                            instance_vars["settings"])
                    dut_dict[interface] = controller_instance
            except Exception:
                pass
        return dut_dict
