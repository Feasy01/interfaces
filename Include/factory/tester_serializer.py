# form ..Include.controllers import DigitalDiscoveryMultiplex
import os
import importlib
import inspect
import pathlib
from ..factory.ControllerParser import ControllerParser
class ControllerFactory:
    @staticmethod
    def generate_controllers_from_cfg(cfg):
        dut_dict = {}
        available_controllers:dict = ControllerParser.dict_of_controllers()
        for x in cfg.keys():
            try:
                class_name,instance_vars = cfg[x].popitem()
                # print(class_name,instance_vars)
                if class_name in available_controllers:
                    print(class_name)
                    instance = available_controllers[class_name].assign_instance(**instance_vars)
                    dut_dict[x] = instance
            except Exception:
                pass
        return
            # print(self._cfg[x])
