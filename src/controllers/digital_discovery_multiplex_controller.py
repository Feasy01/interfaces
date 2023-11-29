from src.controllers.base_controller import BaseController
from src.interface.base_interface import Settings
from ..interface.can import CAN,CANSettings
from ..interface.i2c import I2C,I2CSettings
from ..interface.spi import SPI, SPISettings
from ..interface.uart import UART, UARTSettings
from ..interface.qspi import QSPI, QSPISettings
from ctypes import *
from .include.dwfconstants import *
import math
import sys
import time
import asyncio

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
        #TODO handle case when there are multiple discovery available


    def __del__(self):
        dwf.FDwfDeviceClose(self.hdwf)

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

    def read_i2c(self,device,size,address:c_ubyte = 0x1D)->(bool, bytes):
        iNak = c_int()
        self._configure_i2c(self.settings[device],iNak)
        rgRX = (c_ubyte*size)()
       
#                               8bit address  
        while(1):
            # print(iNak.value)
            dwf.FDwfDigitalI2cRead(self.hdwf, c_int(address<<1), rgRX, c_int(size), byref(iNak)) # read 16 bytes
            time.sleep(0.001)
            print(list(rgRX))

#         print(list(rgRX))
        return (True,b'returned value')


    def write_i2c(self,device:str,data:(c_ubyte),address:c_ubyte = 0x1D)->(bool, bytes):
        iNak = c_int()
        self._configure_i2c(self.settings[device],iNak)
        rgTX:[c_ubyte] = (c_ubyte*len(data))(*data)
        iNak:c_int = c_int()
        dwf.FDwfDigitalI2cWrite(self.hdwf, c_int(address<<1), rgTX, c_int(len(data)), byref(iNak)) # write 16 bytes
    def spy_i2c(self,device,size) -> [c_ubyte]:
        iNak = c_int()
        self._configure_i2c(self.settings[device],iNak)
        dwf.FDwfDigitalI2cSpyStart(self.hdwf)
        nData = 8
        fStart = c_int()
        fStop = c_int()
        rgData = (c_ubyte*nData)()
        cData = c_int()
        while True:
            cData.value = nData
            if dwf.FDwfDigitalI2cSpyStatus(self.hdwf, byref(fStart), byref(fStop), byref(rgData), byref(cData), byref(iNak)) == 0:
                print("Communication with the device failed.")
                szerr = create_string_buffer(512)
                dwf.FDwfGetLastErrorMsg(szerr)
                print(str(szerr.value))
                break
            
            msg = []
            if fStart.value == 1: 
                msg.append("Start")
            elif fStart.value == 2:
                msg.append("ReStart")
                
            for i in range(cData.value):
                # first data is address when fStart is not zero
                if i == 0 and fStart.value != 0:
                    msg.append(hex(rgData[i]>>1))
                    if rgData[i]&1:
                        msg.append("RD")
                    else:
                        msg.append("WR")
                    msg.append(hex(rgData[i]))
                    
            if fStop.value != 0: 
                msg.append("Stop")
            
            # NAK of data index + 1 or negative error
            if iNak.value > 0: 
                msg.append("NAK: "+str(iNak.value))
            elif iNak.value < 0:
                msg.append("Error: "+str(iNak.value))
            
            if len(msg):
                return(msg)
            time.sleep(0.001)
    
    
    
    def read_spi(self,device:str,size:int)->(bool, bytes):
        self._configure_spi(self.settings[device])
        rgbRX = (c_ubyte*size)()
        dwf.FDwfDigitalSpiRead(self.hdwf, c_int(1), c_int(8), rgbRX, c_int(len(rgbRX))) # read array of 8 bit (byte) length elements
        return (True,b'returned value')


    def write_spi(self,device:str,size:int, data:[c_ubyte])-> ([c_ubyte],[c_ubyte]):
        self._configure_spi(self.settings[device])
        rgbTX = (c_ubyte*size)(data)
        dwf.FDwfDigitalSpiWrite(self.hdwf, c_int(1), c_int(8), rgbTX, c_int(len(rgbTX))) # write array of 8 bit (byte) length elements
    async def spy_spi(self,device,nSamples):
        rgdwSamples = (c_uint32*nSamples)()
        cAvailable = c_int()
        cLost = c_int()
        cCorrupted = c_int()
        sts = c_byte()

        # 0 represents DIO-24 with order 1
        idxCS = self.settings[device].cs-24# DIO-24
        idxClk = self.settings[device].clk-24 # DIO-25
        idxMosi = self.settings[device].mosi-24# DIO-26
        idxMiso = self.settings[device].miso-24# DIO-27
        nBits = 8   

        print("Configuring SPI spy...")
        # record mode
        dwf.FDwfDigitalInAcquisitionModeSet(self.hdwf, acqmodeRecord)
        # for sync mode set divider to -1 
        dwf.FDwfDigitalInDividerSet(self.hdwf, c_int(-1))
        # 32bit per sample format
        dwf.FDwfDigitalInSampleFormatSet(self.hdwf, c_int(32))
        # noise samples
        dwf.FDwfDigitalInSampleModeSet(self.hdwf, c_int(1)) 
        # continuous sampling 
        dwf.FDwfDigitalInTriggerPositionSet(self.hdwf, c_int(-1))
        # in sync mode the trigger is used for sampling condition
        # trigger detector mask:          low &     high    & ( rising                     | falling )
        dwf.FDwfDigitalInTriggerSet(self.hdwf, c_int(0), c_int(0), c_int((1<<idxClk)|(1<<idxCS)), c_int(0))
        # sample on clock rising edge for sampling bits, or CS rising edge to detect frames

        # for Digital Discovery bit order: DIO24:39; with 32 bit sampling [DIO24:39 + DIN0:15]
        dwf.FDwfDigitalInInputOrderSet(self.hdwf, c_int(1))

        dwf.FDwfDigitalInConfigure(self.hdwf, c_int(0), c_int(1))

        try:
            fsMosi = 0
            fsMiso = 0
            cBit = 0
            rgMosi = []
            rgMiso = []
            while True:
                
                dwf.FDwfDigitalInStatus(self.hdwf, c_int(1), byref(sts))
                dwf.FDwfDigitalInStatusRecord(self.hdwf, byref(cAvailable), byref(cLost), byref(cCorrupted))

                if cLost.value :
                    print("Samples were lost!")
                if cCorrupted.value :
                    print("Samples could be corrupted!")
                if cAvailable.value > nSamples :
                    cAvailable = c_int(nSamples)
                
                dwf.FDwfDigitalInStatusData(self.hdwf, rgdwSamples, c_int(cAvailable.value*4)) # 32bit data
                
                for i in range(cAvailable.value):
                    v = rgdwSamples[i]
                    if (v>>idxCS)&1: # CS high, inactive, print data
                        if len(rgMosi) != 0 :
                            print(rgMosi)
                            print("MOSI:", end=" ")
                            for j in range(len(rgMosi)) :
                                print("h%02X," % rgMosi[j], end=" ")
                            print("")
                        if len(rgMiso) != 0 :
                            print(rgMiso)
                            print("MISO:", end=" ")
                            for j in range(len(rgMiso)) :
                                print("h%02X," % rgMiso[j], end=" ")
                            print("")
                        if cBit != 0: # log leftover bits, frame not multiple of nBits
                            print("leftover bits %d : h%02X | h%02X" % (cBit, fsMosi, fsMiso))
                        cBit = 0
                        fsMosi = 0
                        fsMiso = 0
                        return (rgMosi,rgMiso)
                    else:
                        cBit+=1
                        fsMosi <<= 1 # MSB first
                        fsMiso <<= 1 # MSB first
                        if (v>>idxMosi)&1 :
                            fsMosi |= 1
                        if (v>>idxMiso)&1 :
                            fsMiso |= 1
                        if cBit >= nBits: # got nBits of bits
                            rgMosi.append(fsMosi)
                            rgMiso.append(fsMiso)
                            cBit = 0
                            fsMosi = 0
                            fsMiso = 0
                asyncio.sleep(1)
        except KeyboardInterrupt:
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
    def write_qspi(self,device:str,data:[c_ubyte]) -> None:
        self._configure_qspi(self.settings[device])
        rgbTX = (c_ubyte*len(data))(*data)
        dwf.FDwfDigitalSpiWrite(self.hdwf, c_int(3), c_int(8), rgbTX, c_int(len(rgbTX))) # write array of 8 bit (byte) length elements
       
    def read_qspi(self,device:str,size) -> None:
        self._configure_spi(self.settings[device])
        rgbRX = (c_ubyte*size)()
        dwf.FDwfDigitalSpiRead(self.hdwf, c_int(3), c_int(8), rgbRX, c_int(len(rgbRX))) # read array of 8 bit (byte) length elements
        return (True,b'returned value')


    def _configure_can(self,settings:CANSettings)-> None:
        dwf.FDwfDigitalCanReset(self.hdwf)
        dwf.FDwfDigitalCanRateSet(self.hdwf, c_double(settings.frequency)) # 1MHz
        dwf.FDwfDigitalCanPolaritySet(self.hdwf, c_int(0)) # normal
        dwf.FDwfDigitalCanTxSet(self.hdwf, c_int(settings.tx)) # TX 
        dwf.FDwfDigitalCanRxSet(self.hdwf, c_int(settings.rx)) # RX 
        dwf.FDwfDigitalCanTx(self.hdwf, c_int(-1), c_int(0), c_int(0), c_int(0), None) # initialize TX, drive with idle level
#                    HDWF *ID   *Exte *Remo *DLC  *rgRX  cRX      *Status 0 = no data, 1 = data received, 2 = bit stuffing error, 3 = CRC error
        dwf.FDwfDigitalCanRx(self.hdwf, None, None, None, None, None, c_int(0), None) # initialize RX reception
        print('some settings not defined for can, please see the documentation and make sure the config file follows it.')

    def _configure_i2c(self,settings:I2CSettings,iNak:c_int)->None:
        dwf.FDwfDigitalI2cReset(self.hdwf)
        dwf.FDwfDigitalI2cRateSet(self.hdwf, c_double(settings.frequency))# frequency
        dwf.FDwfDigitalI2cSclSet(self.hdwf, c_int(settings.scl)) # SCL = DIO-0
        dwf.FDwfDigitalI2cSdaSet(self.hdwf, c_int(settings.sda)) # SDA = DIO-1
        dwf.FDwfDigitalI2cClear(self.hdwf, byref(iNak))
        if iNak.value == 0:
            print("I2C bus error. Check the pull-ups.")
    def _configure_spi(self,settings:SPISettings) -> None:
        dwf.FDwfDigitalSpiReset(self.hdwf)
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
        dwf.FDwfDigitalSpiReset(self.hdwf)
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
        dwf.FDwfDigitalUartReset(self.hdwf)
        # configure the I2C/TWI, default settings
        dwf.FDwfDigitalUartRateSet(self.hdwf, c_double(settings.frequency)) # 9.6kHz
        dwf.FDwfDigitalUartTxSet(self.hdwf, c_int(settings.tx)) # TX = DIO-0
        dwf.FDwfDigitalUartRxSet(self.hdwf, c_int(settings.rx))# RX = DIO-1
        dwf.FDwfDigitalUartBitsSet(self.hdwf, c_int(8)) # 8 bits
        dwf.FDwfDigitalUartParitySet(self.hdwf, c_int(0)) # 0 no parity, 1 even, 2 odd, 3 mark (high), 4 space (low)
        dwf.FDwfDigitalUartStopSet(self.hdwf, c_double(1)) # 1 bit stop length
        dwf.FDwfDigitalUartTx(self.hdwf, None, c_int(0))# initialize TX, drive with idle level
        dwf.FDwfDigitalUartRx(self.hdwf, None, c_int(0), byref(cRX), byref(fParity))# initialize RX reception