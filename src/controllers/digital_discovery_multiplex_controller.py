from src.controllers.base_controller import BaseController
from src.interface.base_interface import Settings
from ..interface.can import CAN,CANSettings
from ..interface.i2c import I2C,I2CSettings
from ..interface.spi import SPI, SPISettings
from ..interface.uart import UART, UARTSettings
from ..interface.qspi import QSPI, QSPISettings
from ctypes import *
import math
import sys
import time
dwf:CDLL = cdll.LoadLibrary("libdwf.so")

class DigitalDiscoveryMultiplexController(CAN,I2C,UART,SPI,QSPI,BaseController):
    exisiting_instances:dict = {}
    """
    Kontroller do Digital dicovery + multiplex
    Klasa jest fabryka obiektow, trzyma instancje w wewnetrznej pamieci i zwraca wskazniki do nich
    """ 

    # @classmethod
    # def assign_instance(cls,
    #                     interface:str, 
    #                     id:int,
    #                     settings:dict) -> object:
    #     if id in cls.exisiting_instances:
    #         cls.exisiting_instances[id].settings[interface]=settings
    #         return cls.exisiting_instances[id]
    #     else:
    #         instance = cls.__new__(cls)
    #         instance._init(interface,id,settings)
    #         cls.exisiting_instances[id]=instance
    #         return instance

    def __init__(self):
        super().__init__()
        self.hdwf:c_int = c_int()
        dwf.FDwfDeviceOpen(c_int(-1), byref(self.hdwf))
        if self.hdwf.value == 0:
            szerr:[c_char] = create_string_buffer(512)
            dwf.FDwfGetLastErrorMsg(szerr)
            assert 0,(str(szerr.value))

    def register_device(self, interface_name:str, settings:Settings):
        super().register_device(interface_name,settings)


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
        self._configure_i2c(self.settings[device],iNak)
        rgRX = (c_ubyte*size)()
#                               8bit address  
        dwf.FDwfDigitalI2cRead(self.hdwf, c_int(address<<1), rgRX, c_int(size), byref(iNak)) # read 16 bytes
        if iNak.value != 0:
            print("NAK "+str(iNak.value))
        print(list(rgRX))
        return (True,b'returned value')


    def write_i2c(self,device:str,data:(c_ubyte),address:c_ubyte = 0x1D)->(bool, bytes):
        iNak = c_int()
        self._configure_i2c(self.settings[device],iNak)
        rgTX:[c_ubyte] = (c_ubyte*len(data))(*data)
        iNak:c_int = c_int()
        dwf.FDwfDigitalI2cWrite(self.hdwf, c_int(address<<1), rgTX, c_int(len(data)), byref(iNak)) # write 16 bytes
        pass

    def read_spi(self,device:str,size:int)->(bool, bytes):
        self._configure_spi(self.settings[device])
        rgbRX = (c_ubyte*size)()
        dwf.FDwfDigitalSpiRead(self.hdwf, c_int(1), c_int(8), rgbRX, c_int(len(rgbRX))) # read array of 8 bit (byte) length elements
        return (True,b'returned value')


    def write_spi(self,device:str,size:int, data:c_byte)->bool:
        self._configure_spi(self.settings[device])
        rgbTX = (c_ubyte*size)(data)
        dwf.FDwfDigitalSpiWrite(self.hdwf, c_int(1), c_int(8), rgbTX, c_int(len(rgbTX))) # write array of 8 bit (byte) length elements
        pass

    def read_uart(self,device:str,size:int)->(bool, bytes):
        fParity = c_int()
        cRX = c_int()
        self._configure_uart(self.settings[device],cRX,fParity)
        rgRX = create_string_buffer(size)
        
        tsec = time.perf_counter()  + 10 # receive for 10 seconds
        print("Receiving on RX...")
        while time.perf_counter() < tsec:
            time.sleep(0.01)
            dwf.FDwfDigitalUartRx(self.hdwf, rgRX, c_int(sizeof(rgRX)-1), byref(cRX), byref(fParity)) # read up to 8k chars at once
            if cRX.value > 0:
                rgRX[cRX.value] = 0 # add zero ending
                print(rgRX.value.decode(), end = '', flush=True)
            if fParity.value != 0:
                print("Parity error {}".format(fParity.value))

        return (True,b'returned value')

    def write_uart(self,device:str,data:str)->bool:
        fParity= c_int()
        cRX = c_int()
        self._configure_uart(self.settings[device],cRX,fParity)
        rgTX = create_string_buffer(f'{data}')
        dwf.FDwfDigitalUartTx(self.hdwf, rgTX, c_int(sizeof(rgTX)-1)) # send text, trim zero ending
        pass
    def write_qspi(self,settings:QSPISettings) -> None:
        pass
    def read_qspi(self,settings:QSPISettings) -> None:
        pass



    def _configure_can(self,settings:CANSettings)-> None:
        try:
            dwf.FDwfDigitalCanRateSet(self.hdwf, c_double(settings.frequency)) # 1MHz
            dwf.FDwfDigitalCanPolaritySet(self.hdwf, c_int(0)) # normal
            dwf.FDwfDigitalCanTxSet(self.hdwf, c_int(settings.tx)) # TX 
            dwf.FDwfDigitalCanRxSet(self.hdwf, c_int(settings.rx)) # RX 
            dwf.FDwfDigitalCanTx(self.hdwf, c_int(-1), c_int(0), c_int(0), c_int(0), None) # initialize TX, drive with idle level
    #                    HDWF *ID   *Exte *Remo *DLC  *rgRX  cRX      *Status 0 = no data, 1 = data received, 2 = bit stuffing error, 3 = CRC error
            dwf.FDwfDigitalCanRx(self.hdwf, None, None, None, None, None, c_int(0), None) # initialize RX reception
        except KeyError:
            print('some settings not defined for can, please see the documentation and make sure the config file follows it.')

    def _configure_i2c(self,settings:I2CSettings,iNak:c_int)->None:
        dwf.FDwfDigitalI2cRateSet(self.hdwf, c_double(settings.frequency))# frequency
        dwf.FDwfDigitalI2cSclSet(self.hdwf, c_int(settings.scl)) # SCL = DIO-0
        dwf.FDwfDigitalI2cSdaSet(self.hdwf, c_int(settings.sda)) # SDA = DIO-1
        dwf.FDwfDigitalI2cClear(self.hdwf, byref(iNak))
        if iNak.value == 0:
            print("I2C bus error. Check the pull-ups.")
    def _configure_spi(self,settings:SPISettings) -> None:
        dwf.FDwfDigitalSpiFrequencySet(self.hdwf, c_double(settings.frequency))
        dwf.FDwfDigitalSpiClockSet(self.hdwf, c_int(settings.clk))
        dwf.FDwfDigitalSpiDataSet(self.hdwf, c_int(0), c_int(settings.mosi)) # 0 DQ0_MOSI_SISO 
        dwf.FDwfDigitalSpiDataSet(self.hdwf, c_int(1), c_int(settings.miso)) # 1 DQ1_MISO 
        dwf.FDwfDigitalSpiIdleSet(self.hdwf, c_int(0), c_int(settings.mosi)) # 0 DQ0_
        dwf.FDwfDigitalSpiIdleSet(self.hdwf, c_int(1), c_int(settings.miso)) # 0 DQ0_
        dwf.FDwfDigitalSpiModeSet(self.hdwf, c_int(0)) # SPI mode 
        dwf.FDwfDigitalSpiOrderSet(self.hdwf, c_int(1)) # 1 MSB first
        dwf.FDwfDigitalSpiSelectSet(self.hdwf, c_int(0), c_int(settings.cs)) # CS DIO-0, idle high
        dwf.FDwfDigitalSpiWriteOne(self.hdwf, c_int(1), c_int(0), c_int(0)) # start driving the channels, clock and data

    def _configure_qspi(self,settings:QSPISettings) -> None:
        dwf.FDwfDigitalSpiFrequencySet(self.hdwf, c_double(settings.frequency))
        dwf.FDwfDigitalSpiClockSet(self.hdwf, c_int(settings.clk))
        dwf.FDwfDigitalSpiDataSet(self.hdwf, c_int(0), c_int(settings.dq0))# 0 DQ0_MOSI_SISO = 
        dwf.FDwfDigitalSpiDataSet(self.hdwf, c_int(1), c_int(settings.dq1)) # 1 DQ1_MISO = 
        dwf.FDwfDigitalSpiDataSet(self.hdwf, c_int(2), c_int(settings.dq2)) # 2 DQ2 
        dwf.FDwfDigitalSpiDataSet(self.hdwf, c_int(3), c_int(settings.dq3)) # 3 DQ3 
        dwf.FDwfDigitalSpiModeSet(self.hdwf, c_int(0)) # SPI mode 
        dwf.FDwfDigitalSpiOrderSet(self.hdwf, c_int(1)) # 1 MSB first
        #                             DIO       value: 0 low, 1 high, -1 high impedance
        dwf.FDwfDigitalSpiSelectSet(self.hdwf, c_int(0), c_int(settings.cs)) #            # cDQ 0 SISO, 1 MOSI/MISO, 2 dual, 4 quad, // 1-32 bits / word
        #                                cDQ       bits     data
        dwf.FDwfDigitalSpiWriteOne(self.hdwf, c_int(4), c_int(0), c_int(0)) # start driving the channels
    def _configure_uart(self,settings:UARTSettings,cRX,fParity) -> None:        
        # configure the I2C/TWI, default settings
        dwf.FDwfDigitalUartRateSet(self.hdwf, c_double(settings.frequency)) # 9.6kHz
        dwf.FDwfDigitalUartTxSet(self.hdwf, c_int(settings.tx)) # TX = DIO-0
        dwf.FDwfDigitalUartRxSet(self.hdwf, c_int(settings.rx))# RX = DIO-1
        dwf.FDwfDigitalUartBitsSet(self.hdwf, c_int(8)) # 8 bits
        dwf.FDwfDigitalUartParitySet(self.hdwf, c_int(0)) # 0 no parity, 1 even, 2 odd, 3 mark (high), 4 space (low)
        dwf.FDwfDigitalUartStopSet(self.hdwf, c_double(1)) # 1 bit stop length
        dwf.FDwfDigitalUartTx(self.hdwf, None, c_int(0))# initialize TX, drive with idle level
        dwf.FDwfDigitalUartRx(self.hdwf, None, c_int(0), byref(cRX), byref(fParity))# initialize RX reception