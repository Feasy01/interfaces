from src.controllers.base_controller import BaseController
from src.interface.base_interface import Settings
from ..interface.can import CAN, CANSettings
from ..interface.i2c import I2C, I2CSettings
from ..interface.spi import SPI, SPISettings
from ..interface.uart import UART, UARTSettings
from ..interface.qspi import QSPI, QSPISettings
from ..interface.gpio import GPIO, GPIOSettings


from ctypes import (
    c_ubyte,
    byref,
    c_int,
    c_uint32,
    c_double,
    cdll,
    CDLL,
    c_char,
    create_string_buffer,
    c_byte,
    sizeof,
)
from typing import List
from .include.dwfconstants import *
import time
import asyncio
from functools import reduce

dwf: CDLL = cdll.LoadLibrary("libdwf.so")


class DigitalDiscoveryMultiplexController(
    BaseController, CAN, I2C, UART, SPI, QSPI, GPIO
):
    """
    Kontroller do Digital dicovery + multiplex
    Klasa jest fabryka obiektow, trzyma instancje w wewnetrznej pamieci i zwraca wskazniki do nich
    """

    # TODO handle case when there are multiple discovery available
    def __init__(self):
        super().__init__()
        self.hdwf: c_int = c_int()
        dwf.FDwfDeviceOpen(c_int(-1), byref(self.hdwf))
        if self.hdwf.value == 0:
            szerr: [c_char] = create_string_buffer(512)
            dwf.FDwfGetLastErrorMsg(szerr)
            assert 0, str(szerr.value)

    def __del__(self):
        dwf.FDwfDeviceClose(self.hdwf)

    def register_device(self, interface_name: str, settings: Settings):
        super().register_device(interface_name, settings)

    # TODO change print to return when there is an eval board to test with
    async def read_can(self, device: CANSettings) -> (bool, bytes):
        self._configure_can(device)
        vID = c_int()
        fExtended = c_int()
        fRemote = c_int()
        cDLC = c_int()
        vStatus = c_int()
        rgbRX = (c_ubyte * 8)()
        tsec = time.clock() + 10  # receive for 10 seconds
        print("Receiving on RX for 10 seconds...")
        while time.clock() < tsec:
            asyncio.sleep(0.01)
            #                    HDWF *ID          *Extended        *Remote         *DLC         *rgRX   cRX                  *Status
            dwf.FDwfDigitalCanRx(
                self.hdwf,
                byref(vID),
                byref(fExtended),
                byref(fRemote),
                byref(cDLC),
                rgbRX,
                c_int(sizeof(rgbRX)),
                byref(vStatus),
            )
            if vStatus.value != 0:
                print(
                    "RX: "
                    + ("0x{:08x}".format(vID.value))
                    + " "
                    + ("Extended " if fExtended.value != 0 else "")
                    + ("Remote " if fRemote.value != 0 else "")
                    + "DLC: "
                    + str(cDLC.value)
                )
                if vStatus.value == 1:
                    print("no error")
                elif vStatus.value == 2:
                    print("bit stuffing error")
                elif vStatus.value == 3:
                    print("CRC error")
                else:
                    print("error")
                if fRemote.value == 0 and cDLC.value != 0:
                    print(
                        "Data: "
                        + (
                            " ".join(
                                "0x{:02x}".format(c) for c in rgbRX[0 : cDLC.value]
                            )
                        )
                    )
        return (True, b"returned value")

    # TODO rozwazyc czy writing moze byc blkoujacy czy ma byc nonblocking
    def write_can(self, device: CANSettings, data: List[int]) -> bool:
        self._configure_can(device)
        rgbTX = (c_ubyte * len(data))(*data)
        print("Sending on TX...")
        #                    HDWF  ID           fExtended  fRemote   cDLC              *rgTX
        dwf.FDwfDigitalCanTx(
            self.hdwf, c_int(0x3FD), c_int(0), c_int(0), c_int(len(rgbTX)), rgbTX
        )
        return True

    async def read_i2c(
        self, device: I2CSettings, size: int, address: int = 0x1D
    ) -> (bool, List[int]):
        iNak = c_int()
        self._configure_i2c(device, iNak)
        rgRX = (c_ubyte * size)()

        while 1:
            dwf.FDwfDigitalI2cRead(
                self.hdwf, c_int(address << 1), rgRX, c_int(size), byref(iNak)
            )
            if len(rgRX) > 1:
                break
            await asyncio.sleep(0.001)

        return (True, list(rgRX))

    def write_i2c(self, device: I2CSettings, data: List[int], address: int = 0x1D) -> bool:
        iNak = c_int()
        self._configure_i2c(device, iNak)
        rgTX: [c_ubyte] = (c_ubyte * len(data))(*data)
        address = (c_ubyte)(address)
        iNak: c_int = c_int()
        dwf.FDwfDigitalI2cWrite(
            self.hdwf, c_int(address << 1), rgTX, c_int(len(data)), byref(iNak)
        )  # write len(data) bytes
        return True

    async def spy_i2c(
        self, device: I2CSettings, nTransactions: int, timeout: int = 30
    ) -> List[str]:
        response = []
        iNak = c_int()
        self._configure_i2c(device, iNak)
        dwf.FDwfDigitalI2cSpyStart(self.hdwf)
        nData = 8
        fStart = c_int()
        fStop = c_int()
        rgData = (c_ubyte * nData)()
        cData = c_int()
        tsec = time.perf_counter() + timeout
        while nTransactions > 0 or time.perf_counter() < tsec:
            cData.value = nData
            if (
                dwf.FDwfDigitalI2cSpyStatus(
                    self.hdwf,
                    byref(fStart),
                    byref(fStop),
                    byref(rgData),
                    byref(cData),
                    byref(iNak),
                )
                == 0
            ):
                print("Communication with the device failed.")
                szerr = create_string_buffer(512)
                dwf.FDwfGetLastErrorMsg(szerr)
                print(str(szerr.value))
                return (False, str(szerr.value))

            msg = []
            if fStart.value == 1:
                msg.append("Start")
            elif fStart.value == 2:
                msg.append("ReStart")

            for i in range(cData.value):
                if i == 0 and fStart.value != 0:
                    msg.append(hex(rgData[i] >> 1))
                    if rgData[i] & 1:
                        msg.append("RD")
                    else:
                        msg.append("WR")
                    msg.append(hex(rgData[i]))

            if fStop.value != 0:
                msg.append("Stop")

            # NAK of data index + 1 or negative error
            if iNak.value > 0:
                msg.append("NAK: " + str(iNak.value))
            elif iNak.value < 0:
                msg.append("Error: " + str(iNak.value))

            if len(msg):
                response.append(msg)
                nTransactions -= 1
            await asyncio.sleep(1)
        return response

    def read_spi(self, device: SPISettings, size: int) -> (bool, List[c_ubyte]):
        self._configure_spi(device)
        rgbRX = (c_ubyte * size)()
        dwf.FDwfDigitalSpiRead(
            self.hdwf, c_int(1), c_int(8), rgbRX, c_int(len(rgbRX))
        )  # read array of 8 bit (byte) length elements
        return (True, list(rgbRX))

    def write_spi(self, device: SPISettings, data: [c_ubyte]) -> ([c_ubyte], [c_ubyte]):
        self._configure_spi(device)
        rgbTX = (c_ubyte * len(data))(*data)
        dwf.FDwfDigitalSpiWrite(
            self.hdwf, c_int(1), c_int(8), rgbTX, c_int(len(rgbTX))
        )  # write array of 8 bit (byte) length elements

    # TODO change never ending reading to reading based on the spy time set
    # TODO handle all 24 pins
    async def spy_spi(self, device: SPISettings, nSamples: int = 100000):
        rgdwSamples = (c_uint32 * nSamples)()
        cAvailable = c_int()
        cLost = c_int()
        cCorrupted = c_int()
        sts = c_byte()

        # 0 represents DIO-24 with order 1
        idxCS: int = device.cs - 24  # DIO-24
        idxClk: int = device.clk - 24  # DIO-25
        idxMosi: int = device.mosi - 24  # DIO-26
        idxMiso: int = device.miso - 24  # DIO-27
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
        # trigger detector mask:          low &     high    & ( rising                    | falling )
        dwf.FDwfDigitalInTriggerSet(
            self.hdwf, c_int(0), c_int(0), c_int((1 << idxClk) | (1 << idxCS)), c_int(0)
        )
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
                dwf.FDwfDigitalInStatusRecord(
                    self.hdwf, byref(cAvailable), byref(cLost), byref(cCorrupted)
                )

                if cLost.value:
                    print("Samples were lost!")
                if cCorrupted.value:
                    print("Samples could be corrupted!")
                if cAvailable.value > nSamples:
                    cAvailable = c_int(nSamples)

                dwf.FDwfDigitalInStatusData(
                    self.hdwf, rgdwSamples, c_int(cAvailable.value * 4)
                )  # 32bit data

                for i in range(cAvailable.value):
                    v = rgdwSamples[i]
                    if (v >> idxCS) & 1:  # CS high, inactive, print data
                        if len(rgMosi) != 0:
                            print(rgMosi)
                            print("MOSI:", end=" ")
                            for j in range(len(rgMosi)):
                                print("h%02X," % rgMosi[j], end=" ")
                            print("")
                        if len(rgMiso) != 0:
                            print(rgMiso)
                            print("MISO:", end=" ")
                            for j in range(len(rgMiso)):
                                print("h%02X," % rgMiso[j], end=" ")
                            print("")
                        if cBit != 0:  # log leftover bits, frame not multiple of nBits
                            print(
                                "leftover bits %d : h%02X | h%02X"
                                % (cBit, fsMosi, fsMiso)
                            )
                        cBit = 0
                        fsMosi = 0
                        fsMiso = 0
                        return (rgMosi, rgMiso)
                    else:
                        cBit += 1
                        fsMosi <<= 1  # MSB first
                        fsMiso <<= 1  # MSB first
                        if (v >> idxMosi) & 1:
                            fsMosi |= 1
                        if (v >> idxMiso) & 1:
                            fsMiso |= 1
                        if cBit >= nBits:  # got nBits of bits
                            rgMosi.append(fsMosi)
                            rgMiso.append(fsMiso)
                            cBit = 0
                            fsMosi = 0
                            fsMiso = 0
                asyncio.sleep(1)
        except KeyboardInterrupt:
            pass

    def read_uart(self, device: UARTSettings, size: int, time: int) -> (bool, bytes):
        fParity = c_int()
        cRX = c_int()
        self._configure_uart(device, cRX, fParity)
        rgRX = create_string_buffer(size)

        tsec = time.perf_counter() + time  # receive for time seconds
        print("Receiving on RX...")
        while time.perf_counter() < tsec:
            asyncio.sleep(0.01)
            dwf.FDwfDigitalUartRx(
                self.hdwf, rgRX, c_int(sizeof(rgRX) - 1), byref(cRX), byref(fParity)
            )  # read up to 8k chars at once
            if cRX.value > 0:
                rgRX[cRX.value] = 0  # add zero ending
                return (True, rgRX.value.decode())
            if fParity.value != 0:
                print("Parity error {}".format(fParity.value))

    def write_uart(self, device: UARTSettings, data: str | List[int]) -> bool:
        fParity = c_int()
        cRX = c_int()
        self._configure_uart(device, cRX, fParity)
        rgTX = (
            create_string_buffer(bytes(data, "utf-8"))
            if isinstance(data, str)
            else create_string_buffer(bytes(data))
        )
        dwf.FDwfDigitalUartTx(
            self.hdwf, rgTX, c_int(sizeof(rgTX) - 1)
        )  # send text, trim zero ending

    def write_qspi(self, device: QSPISettings, data: [c_ubyte]) -> None:
        self._configure_qspi(device)
        rgbTX = (c_ubyte * len(data))(*data)
        dwf.FDwfDigitalSpiWrite(
            self.hdwf, c_int(3), c_int(8), rgbTX, c_int(len(rgbTX))
        )  # write array of 8 bit (byte) length elements

    def read_qspi(self, device: QSPISettings, size: int) -> None:
        self._configure_spi(device)
        rgbRX = (c_ubyte * size)()
        dwf.FDwfDigitalSpiRead(
            self.hdwf, c_int(3), c_int(8), rgbRX, c_int(len(rgbRX))
        )  # read array of 8 bit (byte) length elements
        return (True, b"returned value")

    # TODO handle different sample sizes(like 8 pins, 16pins etc.)

    def read_gpio(self):
        pass

    async def record_gpio(
        self,
        gpios: [GPIOSettings],
        period_ms: int = 500,
        sample_rate: int = 1000000,
        rising_edge: [int] = None,
        falling_edge: [int] = None,
    ) -> [int]:
        # Samples = 100000
        rEdge = (
            reduce(
                lambda x, y: c_int(x.value | y.value),
                [c_int(1 << gpios[device].pin) for device in rising_edge],
                c_int(0),
            )
            if rising_edge
            else c_int(0)
        )
        fEdge = (
            reduce(
                lambda x, y: c_int(x.value | y.value),
                [c_int(1 << gpios[device].pin) for device in falling_edge],
                c_int(0),
            )
            if falling_edge
            else c_int(0)
        )
        print(rEdge, fEdge)
        # rgwSamples = (c_uint16*nSamples)()
        hzDI = c_double()
        sts = c_ubyte()

        dwf.FDwfDigitalInInternalClockInfo(self.hdwf, byref(hzDI))
        print("DigitanIn base freq: " + str(hzDI.value))
        dwf.FDwfDigitalInDividerSet(
            self.hdwf, c_int(int(hzDI.value / sample_rate))
        )  # 100MHz

        nSamples = int((period_ms * sample_rate) / 1000)
        rgwSamples = (c_uint32 * nSamples)()
        print(nSamples, period_ms, sample_rate)
        print("divider", hzDI.value / sample_rate)
        # in record mode samples after trigger are acquired only
        dwf.FDwfDigitalInAcquisitionModeSet(self.hdwf, acqmodeSingle)
        # 16bit per sample format
        dwf.FDwfDigitalInSampleFormatSet(self.hdwf, c_int(32))
        # number of samples after trigger
        dwf.FDwfDigitalInTriggerPositionSet(
            self.hdwf, c_int(int(3 * nSamples / 4))
        )  # trigger in the middle
        # number of samples before trigger
        dwf.FDwfDigitalInTriggerPrefillSet(
            self.hdwf, c_int(nSamples - int(nSamples / 4))
        )
        # set digitalIn as trigger
        dwf.FDwfDigitalInTriggerSourceSet(self.hdwf, trigsrcDetectorDigitalIn)
        # trigger detector mask:                  low &   hight & ( rising | falling )
        dwf.FDwfDigitalInTriggerSet(self.hdwf, c_int(0), c_int(0), rEdge, fEdge)
        # for Digital Discovery bit order: DIO24:39; with 32 bit sampling [DIO24:39 + DIN0:15] or DIN0:23 + DIO24:31 ((1 or 0))
        dwf.FDwfDigitalInInputOrderSet(self.hdwf, c_int(0))
        dwf.FDwfDigitalInBufferSizeSet(self.hdwf, c_int(nSamples))

        # begin acquisition
        dwf.FDwfDigitalInConfigure(self.hdwf, c_int(0), c_int(1))

        print("Recording...")

        while True:
            dwf.FDwfDigitalInStatus(self.hdwf, c_int(1), byref(sts))
            if sts.value == stsDone.value:
                break
            await asyncio.sleep(1)
            print("   done")

        # dwf.FDwfDeviceClose(hdwf)

        dwf.FDwfDigitalInStatusData(self.hdwf, byref(rgwSamples), 4 * nSamples)
        print(list(rgwSamples))
        return list(rgwSamples)

    def _configure_can(self, settings: CANSettings) -> None:
        dwf.FDwfDigitalCanReset(self.hdwf)
        dwf.FDwfDigitalCanRateSet(self.hdwf, c_double(settings.frequency))  # 1MHz
        dwf.FDwfDigitalCanPolaritySet(self.hdwf, c_int(0))  # normal
        dwf.FDwfDigitalCanTxSet(self.hdwf, c_int(settings.tx))  # TX
        dwf.FDwfDigitalCanRxSet(self.hdwf, c_int(settings.rx))  # RX
        dwf.FDwfDigitalCanTx(
            self.hdwf, c_int(-1), c_int(0), c_int(0), c_int(0), None
        )  # initialize TX, drive with idle level
        #                     HDWF *ID   *Exte *Remo *DLC  *rgRX  cRX      *Status 0 = no data, 1 = data received, 2 = bit stuffing error, 3 = CRC error
        dwf.FDwfDigitalCanRx(
            self.hdwf, None, None, None, None, None, c_int(0), None
        )  # initialize RX reception

    def _configure_i2c(self, settings: I2CSettings, iNak: c_int) -> None:
        """
        configures i2c read/write operations -> must be pins24:39 because of i/o support

        Args:
            settings (I2CSettings): to set correct pins and freq
            iNak (c_int): to check the pullups
        """
        print(settings.scl, settings.sda)
        dwf.FDwfDigitalI2cReset(self.hdwf)
        dwf.FDwfDigitalI2cRateSet(self.hdwf, c_double(settings.frequency))  # frequency
        dwf.FDwfDigitalI2cSclSet(self.hdwf, c_int(settings.scl - 24))  # SCL
        dwf.FDwfDigitalI2cSdaSet(self.hdwf, c_int(settings.sda - 24))  # SDA
        dwf.FDwfDigitalI2cClear(self.hdwf, byref(iNak))
        if iNak.value == 0:
            print("I2C bus error. Check the pull-ups.")

    def _configure_spi(self, settings: SPISettings) -> None:
        dwf.FDwfDigitalSpiReset(self.hdwf)
        dwf.FDwfDigitalSpiFrequencySet(self.hdwf, c_double(settings.frequency))  # freq
        dwf.FDwfDigitalSpiClockSet(self.hdwf, c_int(settings.clk))  # clk line
        dwf.FDwfDigitalSpiDataSet(
            self.hdwf, c_int(0), c_int(settings.mosi)
        )  # 0 DQ0_MOSI_SISO
        dwf.FDwfDigitalSpiDataSet(
            self.hdwf, c_int(1), c_int(settings.miso)
        )  # 1 DQ1_MISO
        dwf.FDwfDigitalSpiIdleSet(self.hdwf, c_int(0), c_int(settings.mosi))  # 0 DQ0_
        dwf.FDwfDigitalSpiIdleSet(self.hdwf, c_int(1), c_int(settings.miso))  # 0 DQ1_
        dwf.FDwfDigitalSpiModeSet(self.hdwf, c_int(0))  # SPI mode
        dwf.FDwfDigitalSpiOrderSet(self.hdwf, c_int(1))  # 1 MSB first
        dwf.FDwfDigitalSpiSelectSet(
            self.hdwf, c_int(0), c_int(settings.cs)
        )  # CS, idle high
        dwf.FDwfDigitalSpiWriteOne(
            self.hdwf, c_int(1), c_int(0), c_int(0)
        )  # start driving the channels, clock and data

    def _configure_qspi(self, settings: QSPISettings) -> None:
        dwf.FDwfDigitalSpiReset(self.hdwf)
        dwf.FDwfDigitalSpiFrequencySet(self.hdwf, c_double(settings.frequency))
        dwf.FDwfDigitalSpiClockSet(self.hdwf, c_int(settings.clk))
        dwf.FDwfDigitalSpiDataSet(
            self.hdwf, c_int(0), c_int(settings.dq0)
        )  # 0 DQ0_MOSI_SISO =
        dwf.FDwfDigitalSpiDataSet(
            self.hdwf, c_int(1), c_int(settings.dq1)
        )  # 1 DQ1_MISO =
        dwf.FDwfDigitalSpiDataSet(self.hdwf, c_int(2), c_int(settings.dq2))  # 2 DQ2
        dwf.FDwfDigitalSpiDataSet(self.hdwf, c_int(3), c_int(settings.dq3))  # 3 DQ3
        dwf.FDwfDigitalSpiModeSet(self.hdwf, c_int(0))  # SPI mode
        dwf.FDwfDigitalSpiOrderSet(self.hdwf, c_int(1))  # 1 MSB first
        #                             DIO       value: 0 low, 1 high, -1 high impedance
        dwf.FDwfDigitalSpiSelectSet(
            self.hdwf, c_int(0), c_int(settings.cs)
        )  #            # cDQ 0 SISO, 1 MOSI/MISO, 2 dual, 4 quad, // 1-32 bits / word
        #                                cDQ       bits     data
        dwf.FDwfDigitalSpiWriteOne(
            self.hdwf, c_int(4), c_int(0), c_int(0)
        )  # start driving the channels

    def _configure_uart(self, settings: UARTSettings, cRX, fParity) -> None:
        dwf.FDwfDigitalUartReset(self.hdwf)
        # configure the I2C/TWI, default settings
        dwf.FDwfDigitalUartRateSet(self.hdwf, c_double(settings.frequency))  # 9.6kHz
        dwf.FDwfDigitalUartTxSet(self.hdwf, c_int(settings.tx))  # TX = DIO-0
        dwf.FDwfDigitalUartRxSet(self.hdwf, c_int(settings.rx))  # RX = DIO-1
        dwf.FDwfDigitalUartBitsSet(self.hdwf, c_int(8))  # 8 bits
        dwf.FDwfDigitalUartParitySet(
            self.hdwf, c_int(0)
        )  # 0 no parity, 1 even, 2 odd, 3 mark (high), 4 space (low)
        dwf.FDwfDigitalUartStopSet(self.hdwf, c_double(1))  # 1 bit stop length
        dwf.FDwfDigitalUartTx(
            self.hdwf, None, c_int(0)
        )  # initialize TX, drive with idle level
        dwf.FDwfDigitalUartRx(
            self.hdwf, None, c_int(0), byref(cRX), byref(fParity)
        )  # initialize RX reception
