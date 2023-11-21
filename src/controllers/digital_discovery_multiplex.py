from ..interface.magistrale.can import CAN
from ..interface.magistrale.i2c import I2C
from ..interface.magistrale.spi import SPI
from ..interface.magistrale.uart import UART
from ctypes import *
import math
import sys
import time
dwf:CDLL = cdll.LoadLibrary("libdwf.so")

class DigitalDiscoveryMultiplex(CAN,I2C,UART,SPI):
    exisiting_instances:dict = {}
    """
    Kontroller do Digital dicovery + multiplex
    Klasa jest fabryka obiektow, trzyma instancje w wewnetrznej pamieci i zwraca wskazniki do nich
    """ 
    @classmethod
    def assign_instance(cls,
                        interface:str, 
                        id:int,
                        settings:dict) -> object:
        if id in cls.exisiting_instances:
            cls.exisiting_instances[id].settings[interface]=settings
            return cls.exisiting_instances[id]
        else:
            instance = cls.__new__(cls)
            instance._init(interface,id,settings)
            cls.exisiting_instances[id]=instance
            return instance


    def __init__(self)->None:
        raise NotImplementedError("please use assign_instance classmethod to get an instance of this object")

    def _init(self,
              interface:str,
              id:int,
              settings:dict) -> None:
        self.settings:dict={interface:settings}
        self._id:int = id
        self.hdwf:c_int = c_int()
        dwf.FDwfDeviceOpen(c_int(-1), byref(self.hdwf))
        if self.hdwf.value == 0:
            print("failed to open device")
            szerr:[c_char] = create_string_buffer(512)
            dwf.FDwfGetLastErrorMsg(szerr)
            print(str(szerr.value))

        

    
    
    
    def read_can(self, device) ->(bool, bytes):
        self._configure_can(self.settings[device])
        
        vID  = c_int()
        fExtended  = c_int()
        fRemote  = c_int()
        cDLC = c_int()
        vStatus  = c_int()
        rgbRX = (c_ubyte*8)()
        tsec = time.clock() + 10 # receive for 10 seconds
        print("Receiving on RX for 10 seconds...")
        while time.clock() < tsec:
            time.sleep(0.01)
            #                    HDWF *ID          *Extended        *Remote         *DLC         *rgRX   cRX                  *Status
            dwf.FDwfDigitalCanRx(self.hdwf, byref(vID), byref(fExtended), byref(fRemote), byref(cDLC), rgbRX, c_int(sizeof(rgbRX)), byref(vStatus)) 
            if vStatus.value != 0:
                print("RX: "+('0x{:08x}'.format(vID.value)) +" "+("Extended " if fExtended.value!=0 else "")+("Remote " if fRemote.value!=0 else "")+"DLC: "+str(cDLC.value))
                if vStatus.value == 1:
                    print("no error")
                elif vStatus.value == 2:
                    print("bit stuffing error")
                elif vStatus.value == 3:
                    print("CRC error")
                else:
                    print("error")
                if fRemote.value == 0 and cDLC.value != 0:
                    print("Data: "+(" ".join("0x{:02x}".format(c) for c in rgbRX[0:cDLC.value])))
        return (True,b'returned value')


    def write_can(self,device,data)->bool:
        print(*data)
        self._configure_can(self.settings[device])        
        rgbTX = (c_ubyte*len(data))(*data)

        print("Sending on TX...")
        #                    HDWF  ID           fExtended  fRemote   cDLC              *rgTX
        dwf.FDwfDigitalCanTx(self.hdwf, c_int(0x3FD), c_int(0), c_int(0), c_int(len(rgbTX)), rgbTX) 
        print(rgbTX[0])
        pass


    def read_i2c(self,device,size,address:c_ubyte = 0x1D)->(bool, bytes):
        iNak = c_int()
        self._configure_i2c(self.settings[device],byref(iNak))
        rgRX = (c_ubyte*size)()
#                               8bit address  
        dwf.FDwfDigitalI2cRead(self.hdwf, c_int(address<<1), rgRX, c_int(size), byref(iNak)) # read 16 bytes
        if iNak.value != 0:
            print("NAK "+str(iNak.value))
        print(list(rgRX))
        return (True,b'returned value')


    def write_i2c(self,device:str,data:(c_ubyte),address:c_ubyte = 0x1D)->(bool, bytes):
        iNak = c_int()
        self._configure_i2c(self.settings[device],byref(iNak))
        rgTX:[c_ubyte] = (c_ubyte*len(data))(*data)
        iNak:c_int = c_int()
        dwf.FDwfDigitalI2cWrite(self.hdwf, c_int(address<<1), rgTX, c_int(len(data)), byref(iNak)) # write 16 bytes
        pass

    def read_spi(self,device:str)->(bool, bytes):
        print(f'you just read from {device}, it is defined in controller {self}, at pins {self.settings[device]["pin"]}')
        return (True,b'returned value')


    def write_spi(self)->bool:
        pass

    def read_uart(self)->(bool, bytes):
        pass
        return (True,b'returned value')

    def write_uart(self)->bool:
        pass

    def _configure_can(self,settings)-> None:
        try:
            dwf.FDwfDigitalCanRateSet(self.hdwf, c_double(settings["frequency"])) # 1MHz
            dwf.FDwfDigitalCanPolaritySet(self.hdwf, c_int(0)) # normal
            dwf.FDwfDigitalCanTxSet(self.hdwf, c_int(settings["pin"][0])) # TX 
            dwf.FDwfDigitalCanRxSet(self.hdwf, c_int(settings["pin"][1])) # RX 
            dwf.FDwfDigitalCanTx(self.hdwf, c_int(-1), c_int(0), c_int(0), c_int(0), None) # initialize TX, drive with idle level
    #                    HDWF *ID   *Exte *Remo *DLC  *rgRX  cRX      *Status 0 = no data, 1 = data received, 2 = bit stuffing error, 3 = CRC error
            dwf.FDwfDigitalCanRx(self.hdwf, None, None, None, None, None, c_int(0), None) # initialize RX reception
        except KeyError:
            print('some settings not defined for can, please see the documentation and make sure the config file follows it.')

    def _configure_i2c(self,settings,iNak:c_int)->None:
        dwf.FDwfDigitalI2cRateSet(self.hdwf, c_double(settings["frequency"]))# frequency
        dwf.FDwfDigitalI2cSclSet(self.hdwf, c_int(settings["pin"][0])) # SCL = DIO-0
        dwf.FDwfDigitalI2cSdaSet(self.hdwf, c_int(settings["pin"][0])) # SDA = DIO-1
        dwf.FDwfDigitalI2cClear(self.hdwf, byref(iNak))
        if iNak.value == 0:
            print("I2C bus error. Check the pull-ups.")
    def _configure_spi_dual(self,settings) -> None:
        dwf.FDwfDigitalSpiFrequencySet(self.hdwf, c_double(settings["frequency"]))
        dwf.FDwfDigitalSpiClockSet(self.hdwf, c_int(1))
        dwf.FDwfDigitalSpiDataSet(self.hdwf, c_int(0), c_int(settings["pin"][0])) # 0 DQ0_MOSI_SISO = DIO-2
        dwf.FDwfDigitalSpiDataSet(self.hdwf, c_int(1), c_int(settings["pin"][1])) # 1 DQ1_MISO = DIO-3
        dwf.FDwfDigitalSpiModeSet(self.hdwf, c_int(0)) # SPI mode 
        dwf.FDwfDigitalSpiOrderSet(self.hdwf, c_int(1)) # 1 MSB first
        dwf.FDwfDigitalSpiSelectSet(self.hdwf, c_int(0), c_int(1)) # CS DIO-0, idle high
        dwf.FDwfDigitalSpiWriteOne(self.hdwf, c_int(2), c_int(0), c_int(0)) # start driving the channels, clock and data
