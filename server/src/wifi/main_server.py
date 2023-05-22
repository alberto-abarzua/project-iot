from utils.models import DatabaseManager
from wifi.servers import handshake_server, run_server_on_thread, server_tcp, server_udp



class WifiServer:

    def __init__(self):
        self.DBManager = DatabaseManager()


    def run(self):
        thread = run_server_on_thread(handshake_server)
        self.DBManager.db_init()
        while True:
            print("Starting server")
            # current config
            config = self.DBManager.get_default_config()
            if config.transport_layer == "T":
                server = server_tcp
            else:
                server = server_udp

            thread = run_server_on_thread(server)
            thread.join()
            self.DBManager.db_close()


