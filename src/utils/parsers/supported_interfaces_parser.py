import os
import importlib
import inspect
from types import ModuleType
class InterfacesParser:
    """
    Parsuje folder interfaces zawierajacy sterowniki obslugujace rozne urzadzenia, przekazuje dostepne jako dictionary
    """
    @staticmethod
    def dict_of_interfaces()-> dict:
        class_dict :dict= {}
        path_to_interfaces:str = 'src/interface'
        directory_path:str = os.path.join(os.getcwd(),
                                          path_to_interfaces) 
        for filename in os.listdir(directory_path):
            if filename.endswith(".py") and not filename.startswith("__"):
                module_name = filename[:-3]
                module = importlib.import_module(name = f'src.interface.{module_name}',
                                                package=__package__)
                classes:dict = inspect.getmembers(module,
                                                  inspect.isclass)
                for class_name, class_obj in classes:
                    if class_name.endswith("Settings"): class_dict[class_name] = class_obj 

        return class_dict
    
if __name__ == "__main__":
    print(InterfacesParser.dict_of_interfaces())