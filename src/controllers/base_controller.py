from src.interface.base_interface import Settings

class BaseController:
    def __init__(self):
        self.settings:dict ={}
    def register_device(self,interface_name:str,settings:Settings):
        self.settings[interface_name] = settings