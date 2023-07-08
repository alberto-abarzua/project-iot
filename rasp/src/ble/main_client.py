from ble.utils import BleManager
from utils.general import run_server_on_thread
import os

class BleClient:
    DEVICE_NAME = os.environ.get("BLE_DEVICE_NAME")
    DEVICE_MAC = os.environ.get("BLE_MAC_ADDRESS")
    CHARACTERISTIC_UUID = os.environ.get("BLE_CHARACTERISTIC_UUID")

    def run(self, *args, **kwargs):
        transport_layer = kwargs.get("transport_layer")
        device_manager = BleManager(
            BleClient.DEVICE_NAME,
            BleClient.CHARACTERISTIC_UUID,
            BleClient.DEVICE_MAC,
            transport_layer,
        )
        ble_server = run_server_on_thread(device_manager.run)
        ble_server.join()
