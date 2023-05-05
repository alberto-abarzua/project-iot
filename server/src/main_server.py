from models import db_close, db_init, get_default_config
from servers import handshake_server, run_server_on_thread, server_tcp, server_udp


def main():
    thread = run_server_on_thread(handshake_server)
    db_init()
    while True:
        print("Starting server")
        # current config
        config = get_default_config()
        if config.transport_layer == "T":
            server = server_tcp
        else:
            server = server_udp

        thread = run_server_on_thread(server)
        thread.join()
        db_close()


if __name__ == "__main__":
    main()
