from utils.general import run_server_on_thread
from wifi.servers import WifiServerCore


class WifiServer:
    def run(self, *args, **kwargs):
        wifi_server = WifiServerCore(*args, **kwargs)
        server = run_server_on_thread(wifi_server.run)
        server.join()
        print("Server finished")
