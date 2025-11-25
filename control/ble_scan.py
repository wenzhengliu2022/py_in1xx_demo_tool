import asyncio
import platform
import struct

from PySide6.QtCore import QThread, Signal
from bleak import BleakScanner, BLEDevice, AdvertisementData

from control.app_config import AppConfig


class BLEScannerThread(QThread):
    newData = Signal(float)

    def __init__(self, cfg: AppConfig):
        super().__init__()
        system_str = platform.system()
        if system_str == "Darwin":
            self.is_mac = True
        else:
            self.is_mac = False
        self._loop = asyncio.new_event_loop()
        self.target_addr = "C6:D5:04:03:02:11".upper()
        self.ble_company_id = 0xF119
        self.scanner = None
        self.scan_loop = True
        if 'little' == cfg.data_endian:
            self.data_little_endian = True
        else:
            self.data_little_endian = False
        self.data_offset = cfg.data_offset
        self.temp_slope = cfg.temp_slope
        self.temp_offset = cfg.temp_offset

    def run(self):
        self.scan_loop = True
        asyncio.set_event_loop(self._loop)
        self._loop.run_until_complete(self.scan())

    def detection_callback(self, device: BLEDevice, advertisement_data: AdvertisementData):
        if self.is_mac or device.address.upper() == self.target_addr:
            if advertisement_data.manufacturer_data:
                manufacturer_data = advertisement_data.manufacturer_data
                for key, value in manufacturer_data.items():
                    # print("{} {}".format(type(key), key))
                    # print("{} {}".format(type(value), value.hex()))
                    if self.ble_company_id == key:
                        try:
                            if len(value) >= self.data_offset + 2:
                                # '>h' 表示 大端(>) 有符号短整型(h)
                                if self.data_little_endian:
                                    temperature_raw = struct.unpack('<h', value[self.data_offset:self.data_offset+2])[0]
                                else:
                                    temperature_raw = struct.unpack('>h', value[self.data_offset:self.data_offset+2])[0]
                                print(f"temperature_raw  {temperature_raw}")
                                temperature_celsius = temperature_raw * self.temp_slope + self.temp_offset

                                self.newData.emit(round(temperature_celsius, 1))
                        except Exception as e:
                            print(str(e))

    async def scan(self):
        self.scanner = BleakScanner(detection_callback=self.detection_callback)
        await self.scanner.start()
        while self.scan_loop and self.isRunning():
            await asyncio.sleep(0.1)
        await self.scanner.stop()

    def stop_scan(self):
        self.scan_loop = False
