import os
import importlib
import inspect
class ControllerParser:
    
    @staticmethod
    def dict_of_controllers()-> dict:
        class_dict = {}
        path_to_controllers = 'include/controllers'
        directory_path = os.path.join(os.getcwd(),path_to_controllers) # Replace with the actual path to your directory
        for filename in os.listdir(directory_path):
            if filename.endswith(".py") and not filename.startswith("__"):
                module_name = filename[:-3]  # Remove the ".py" extension
                module = importlib.import_module(name = f'..controllers.{module_name}' ,package=__package__)
                classes = inspect.getmembers(module, inspect.isclass)
                for class_name, class_obj in classes:
                    class_dict[class_name] = class_obj


        return class_dict