from ble.utils import BleManager
import asyncio

class BleClient:
    def run(self):
        DEVICE_NAME = "ESP_GATTS_DEMO"
        CHARACTERISTIC_UUID = "0000ff01-0000-1000-8000-00805F9B34FB"
        device_manager = BleManager(DEVICE_NAME, CHARACTERISTIC_UUID)
        asyncio.run(device_manager.run())

