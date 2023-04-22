import socket
from models import *
import threading
from packet_parser import PacketParser
import time
def recv_util_end(socket):
    length = 28
    data = b''
    while True:
        time.sleep(0.01)
        print("recving",len(data))
        packet = socket.recv(length)
        data += packet
        if len(packet) < length:
            break
        length = 1024
    return data



def server_echo_tcp():
    ECHO_TEST_SERVER_PORT = os.environ.get("ECHO_TEST_SERVER_PORT")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', int(ECHO_TEST_SERVER_PORT)))
    server_socket.listen(5)
    print("Server is listening on port: ", ECHO_TEST_SERVER_PORT)
    while True:
        client_socket, client_address = server_socket.accept()
        print("Connection from: ", client_address)
        while True:
            parser = PacketParser()
            data = recv_util_end(client_socket)
            headers = parser.parse_headers(data)
    

            print("this is len of data", len(data))
            if not data:
                break

            print(parser.parse(data))
            print("Received: ", data)
            client_socket.sendall("ok".encode("utf-8"))

        client_socket.close()



def run_server_on_thread(target_fun):
    proc = threading.Thread(target=target_fun)
    proc.start()
    return proc