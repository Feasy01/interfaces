from ..interface.magistrale.can import CAN
from ..interface.magistrale.i2c import I2C
from ..interface.magistrale.spi import SPI
from ..interface.magistrale.uart import UART


class DigitalDiscoveryMultiplex:
    exisiting_instances:dict = {}
    """
    siema
    """ 
    @classmethod
    def assign_instance(cls,id:int,pin:[int]) -> object:
        if id in cls.exisiting_instances:
            print("passing back exisitng instance of {cls}")
            # do something to pass new pins to exsiting instance of controller
            return cls.exisiting_instances[id]
        else:
            instance = cls.__new__(cls)
            instance._init(id,pin)
            cls.exisiting_instances[id]=instance
            return instance


    def __init__(self, id:int, pin:[int])->None:
        self._id = id
        self._pin = pin
        DigitalDiscoveryMultiplex.exisiting_instances[self._id] = self
        # self._controllerdMagistrals

    def _init(self,id:int,pin:[int]) -> None:
        print("creating new instance of {cls}")
        self._id = id
        self._pin = pin


    