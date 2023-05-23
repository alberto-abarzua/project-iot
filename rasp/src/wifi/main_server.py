from utils.models import DatabaseManager
from wifi.servers import TcpServer, UdpServer , HandShakeServer
from utils.general import run_server_on_thread

class WifiServer:

    def run(self,*args, **kwargs):
        transport_layer = kwargs.get("transport_layer",None)
        server_handshake = HandShakeServer()
        handshake_server = run_server_on_thread(server_handshake.run)
        while True:
            if not handshake_server.is_alive():
                handshake_server = run_server_on_thread(server_handshake.run)
            print("Starting server")
            
            if transport_layer == "T":
                server = TcpServer()
            elif transport_layer == "U":
                server = UdpServer()
            else:
                raise Exception("Invalid transport layer" + transport_layer)
            server = run_server_on_thread(server.run)
            server.join()
            print("Server finished")
