from utils.general import run_server_on_thread
from wifi.servers import WifiServerCore


class WifiServer:
    def run(self,join = True):
        wifi_server = WifiServerCore()
        server = run_server_on_thread(wifi_server.run)
        if join:
            server.join()
        else:
            return server
