from ble.main_client import BleClient
from utils.models import DatabaseManager
from wifi.main_server import WifiServer
from utils.prints import console

def main():
    DatabaseManager.db_init()
    while True:
        config = DatabaseManager.get_default_config()
        transport_layer = config.transport_layer
        if transport_layer == "T" or transport_layer == "U":
            WifiServer().run(transport_layer=transport_layer)
        elif transport_layer == "C" or transport_layer == "D":
            BleClient().run(transport_layer=transport_layer)
        else:
            console.print("Invalid transport layer", style="danger")
            break
        
    DatabaseManager.db_close()


if __name__ == "__main__":
    main()
