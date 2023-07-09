from ble.utils import BleManager
from utils.general import run_server_on_thread
import os


class BleClient:

    DEVICE_NAME = os.environ.get("BLE_DEVICE_NAME")
    CHARACTERISTIC_UUID = os.environ.get("BLE_CHARACTERISTIC_UUID")

    def __init__(self, mac_addr=None):
        if mac_addr is not None:
            self.device_mac = mac_addr
        else:
            self.device_mac = os.environ.get("BLE_MAC_ADDRESS")

    def run(self,join = True):
        device_manager = BleManager(
            BleClient.DEVICE_NAME,
            BleClient.CHARACTERISTIC_UUID,
            self.device_mac,
        )
        ble_server = run_server_on_thread(device_manager.run)
        if join:
            ble_server.join()
        else:
            return ble_server
