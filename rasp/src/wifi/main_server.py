from utils.general import run_server_on_thread
from wifi.servers import HandShakeServer, TcpServer, UdpServer


class WifiServer:
    def run(self, *args, **kwargs):
        transport_layer = kwargs.get("transport_layer", None)
        server_handshake = HandShakeServer()
        handshake_server = run_server_on_thread(server_handshake.run)
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
