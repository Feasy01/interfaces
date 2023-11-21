import os
import importlib
import inspect
from types import ModuleType
class ControllerParser:
    """
    Parsuje folder controllers zawierajacy sterowniki obslugujace rozne urzadzenia, przekazuje dostepne jako dictionary
    """
    @staticmethod
    def dict_of_controllers()-> dict:
        class_dict :dict= {}
        path_to_controllers:str = 'src/controllers'
        directory_path:str = os.path.join(os.getcwd(),
                                          path_to_controllers) 
        for filename in os.listdir(directory_path):
            if filename.endswith(".py") and not filename.startswith("__"):
                module_name = filename[:-3]
                module = importlib.import_module(name = f'src.controllers.{module_name}',
                                                package=__package__)
                classes:dict = inspect.getmembers(module,
                                                  inspect.isclass)
                for class_name, class_obj in classes:
                    class_dict[class_name] = class_obj

        return class_dict