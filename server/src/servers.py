import socket
from models import *
import threading
from packet_parser import PacketParser
import time


def recv_in_chunks_tcp(socket, total, chunk_size=1024):
    data = b''
    while len(data) < total:
        chunk = socket.recv(chunk_size)
        if not chunk:
            break
        data += chunk
    return data


def recv_headers_tcp(socket):
    print("Waiting for headers")
    headers = socket.recv(12)
    return headers


def server_tcp():
    SERVER_PORT_TCP = os.environ.get("SERVER_PORT_TCP")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', int(SERVER_PORT_TCP)))
    server_socket.listen(5)
    print("Server is listening on port: ", SERVER_PORT_TCP)
    while True:
        client_socket, client_address = server_socket.accept()
        print("Connection from: ", client_address)
        parser = PacketParser()
        while True:
            data_headers = recv_headers_tcp(client_socket)
            id_device, mac, transport_layer, id_protocol, message_length = parser.parse_headers(
                data_headers)
            print(id_device, mac, transport_layer, id_protocol, message_length)
            data = recv_in_chunks_tcp(client_socket, message_length)
            body = parser.parse_body(data, id_protocol)
            print(body)
        client_socket.close()


def server_udp():
    SERVER_PORT_UDP = os.environ.get("SERVER_PORT_UDP")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    other_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(('0.0.0.0', int(SERVER_PORT_UDP)))
    print("Server UDP is listening on port: ", SERVER_PORT_UDP)
    while True:
        # send to self
        # other_socket.sendto(b'Hello, world!', ("localhost", int(SERVER_PORT_UDP)))
        data, addr = server_socket.recvfrom(len(b'Hello, world!'))
        print(addr)
        print(data)


def run_server_on_thread(target_fun):
    proc = threading.Thread(target=target_fun)
    proc.start()
    return proc
