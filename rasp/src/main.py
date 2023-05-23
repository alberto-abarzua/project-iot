from ble.main_client import BleClient
from wifi.main_server import WifiServer

MODE = "BLE"


def main():
    print("Starting using", MODE)
    if MODE == "BLE":
        BleClient().run()
    if MODE == "WIFI":
        WifiServer().run()
    else:
        raise Exception("Invalid mode")


if __name__ == "__main__":
    main()
