from ..interface.magistrale.can import CAN
from ..interface.magistrale.i2c import I2C
from ..interface.magistrale.spi import SPI
from ..interface.magistrale.uart import UART


class DigitalDiscoveryMultiplex(CAN,I2C,UART,SPI):
    exisiting_instances:dict = {}
    """
    siema
    """ 
    @classmethod
    def assign_instance(cls,interface:str, id:int,pin:[int],) -> object:
        if id in cls.exisiting_instances:
            # do something to pass new pins to exsiting instance of controller
            cls.exisiting_instances[id].map_of_pins[interface]=pin
            return cls.exisiting_instances[id]
        else:
            instance = cls.__new__(cls)
            instance._init(interface,id,pin)
            cls.exisiting_instances[id]=instance
            return instance


    def __init__(self)->None:
        raise NotImplementedError("please use assign_instance classmethod to get an instance of this object")

    def _init(self,interface:str,id:int,pin:[int]) -> None:
        print("creating new instance of {self}")
        self.map_of_pins:dict={interface:pin}
        self._id:int = id
        self._pin:[int] = pin
    
    
    
    def read_can(self) ->(bool, bytes):
        pass
        return (True,b'returned value')


    def write_can(self)->bool:
        pass


    def read_i2c()->(bool, bytes):
        pass
        return (True,b'returned value')


    def write_i2c()->bool:
        pass

    def read_spi(self,device:str)->(bool, bytes):
        print(f'you just read from {device}, it is defined in controller {self}, at pins {self.map_of_pins[device]}')
        return (True,b'returned value')


    def write_spi(self)->bool:
        pass

    def read_uart(self)->(bool, bytes):
        pass
        return (True,b'returned value')

    def write_uart(self)->bool:
        pass

    