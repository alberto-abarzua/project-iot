import asyncio

from ble.utils import BleManager
from utils.general import run_server_on_thread

class BleClient:
    DEVICE_NAME = "ESP_GATTS_DEMO"
    DEVICE_MAC = 'AC:67:B2:38:41:D2'
    CHARACTERISTIC_UUID = "0000ff01-0000-1000-8000-00805F9B34FB"
    def run(self, *args, **kwargs):
        transport_layer = kwargs.get("transport_layer")
        device_manager = BleManager(BleClient.DEVICE_NAME, BleClient.CHARACTERISTIC_UUID,BleClient.DEVICE_MAC, transport_layer)
        while True:
            ble_server = run_server_on_thread(device_manager.run)
            ble_server.join()
            print("Server finished")
            
