import datetime
import os
import socket
import time
from utils.exceptions import LossException
from utils.models import DatabaseManager, Logs, Loss
from utils.packet_parser import PacketParser
from utils.prints import console

from utils.general import diff_to_now_utc_timestamp, now_utc_timestamp
import errno



class ComunicationCore:

    def __init__(self, server):
        self.server = server
        self.socket = None
        self.timeout = 6
        if server.config.transport_layer == "T" or server.config.transport_layer == "D":
            self.timeout = server.config.discontinuous_time*60
    


    @property
    def addr(self):
        return ("0.0.0.0", int(self.port))

    def send(self, data):
        raise NotImplementedError

    def recv(self):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError

    def start(self):
        raise NotImplementedError


class TcpComunicationCore(ComunicationCore):

    def __init__(self, server):
        super().__init__(server)
        self.con_socket = None
        self.port =  self.server.config.tcp_port


    def start(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.addr)
        self.socket.listen(5)
        console.print(f"Waiting for connection on port {self.port}", style="info")
        while True:
            try:
                self.con_socket, client_address = self.socket.accept()
                self.con_socket.settimeout(self.timeout)
                console.print(f"Connection from: {client_address}", style="info")
                return True
            except TimeoutError:
                console.print("Waiting for connection ...", style="info")

    def send(self, data):
        self.con_socket.send(data)

    def recv(self, num_bytes):
        max_chunk_size = 1024
        data = b""
        while len(data) < num_bytes:
            chunk_size = min(max_chunk_size, num_bytes - len(data))
            console.print(f"current_chunk_size: {chunk_size}", style="info")
            try:
                chunk = self.con_socket.recv(chunk_size)
            except TimeoutError:
                console.print("Timeout error, packets lost ...", style="error")
                raise LossException(num_bytes - len(data))
            if not chunk:
                break
            data += chunk            
            console.print(f"Received {len(data)} bytes out of {num_bytes}, bytes left {num_bytes - len(data)}", style="info")
        return data

    def close(self):
        for sock in [self.con_socket, self.socket]:
            try:
                sock.shutdown(socket.SHUT_RDWR)
                sock.close()
                console.print("Socket closed", style="info")
            except OSError as e:
                console.print(f"Error closing socket: {e}", style="error")
                if e.errno not in {errno.ENOTCONN, errno.EBADF}:  # Ignore errors that indicate the socket is already closed
                    raise  # Reraaise other errors
        return True


class UdpComunicationCore(ComunicationCore):

    def __init__(self, server):
        super().__init__(server)
        self.socket = None
        self.client_addr = None
        self.port =  self.server.config.udp_port


    def start(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.addr)
        self.socket.settimeout(self.timeout)
        return True

    def send(self, data):
        if self.client_addr:
            console.print(f"Sending data to {self.client_addr}", style="info")
            self.socket.sendto(data, self.client_addr)
        else:
            raise Exception("No client address")

    def recv(self, num_bytes):
        max_chunk_size = 1024
        data = b""
        while len(data) < num_bytes:
            console.log(f"Waiting for {num_bytes - len(data)} bytes", style="light_info")
            chunk_size = min(max_chunk_size, num_bytes - len(data))
            try:
                chunk, self.client_addr = self.socket.recvfrom(chunk_size)
                time.sleep(0.01)
            except TimeoutError:
                console.print("Timeout error, packets lost ...", style="error")
                raise LossException(num_bytes - len(data))
            if not chunk:
                break
            data += chunk
        return data

    def close(self):
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()
        console.print("Connection closed", style="info")
        return True


class WifiServerCore:

    def __init__(self):

        self.config = DatabaseManager.get_default_config()

        self.transport_layer = self.config.transport_layer
        self.protocol_id = self.config.protocol_id
        self.parser = PacketParser()
        self.tries = 1
        self.init_timestamp = datetime.datetime.utcnow()
        self.init_timestamp = self.init_timestamp.replace(
            tzinfo=datetime.timezone.utc
        ).timestamp()

        if self.transport_layer == "T" or self.transport_layer == "K":
            self.server = TcpComunicationCore(self)

        elif self.transport_layer == "U":
            self.server = UdpComunicationCore(self)

    def read_data(self):
        console.log("Waiting for data ...", style="info")
        try:
            data_headers = self.server.recv(12)
            headers = self.parser.parse_headers(data_headers)
            _, _, _, protocol_id, message_length = headers
            body_data = self.server.recv(message_length)
            
            body = self.parser.parse_body(
                body_data, protocol_id)

            DatabaseManager.save_data_to_db(headers, body)
            console.print("Data saved to db", style="info")
        except LossException as e:
            console.print(f"Loss exception!!!! {e}", style="error")
            bytes_lost = e.bytes_lost
            Loss.create(
                data=None,
                bytes_lost=bytes_lost,
                latency=0,
            ).save()
            self.server.close()
            exit(1)
        except OSError as e:
            console.print("Error during connection!", style="error")
            console.print(e, style="error")
            self.server.close()
            exit(1)


    def handshake(self):

        first_headers = self.server.recv(12)
        console.print(f"Handshake_headers: {first_headers} of len {len(first_headers)}", style="info")
        id_device,_,transport_layer,protocol_id,message_length = self.parser.parse_headers(first_headers)
        body = self.server.recv(message_length)
        body = self.parser.parse_body(body, protocol_id)

        console.print(f"Handshake received from device {id_device} using {transport_layer} - Protocol {protocol_id} ", style="info")
        

        dif = diff_to_now_utc_timestamp(body[1])
        now = now_utc_timestamp()

        if self.init_timestamp is not None:
            time_to_connect = now - self.init_timestamp
            tries = self.tries

            log = Logs.create(
                timestamp=now,
                id_device=id_device,
                custom_epoch=dif,
                time_to_connect=time_to_connect,
                protocol_id=protocol_id,
                transport_layer=transport_layer,
                tries=tries,
                ble_state_machine="wifi",
            )
            log.save()
            console.print("Log saved!", style="info")
            self.init_timestamp = None

        current_config = DatabaseManager.get_default_config()

        changed = current_config.was_changed(self.transport_layer,self.protocol_id)
        self.server.send(self.parser.pack_config(current_config)) 

        if changed:
            console.print("Config was modified!", style="error")
            self.server.close()
            exit(1)
        console.print("Sending config to device", style="info")
        
        
    def run(self):
        self.start_time = datetime.datetime.utcnow()
        console.print(f"Starting server using {self.transport_layer} - Protocol {self.protocol_id} ", style="info")
        time.sleep(1)
        self.server.start()
        console.print("Server started", style="info")
        if self.transport_layer == "U":
            self.server.socket.settimeout(None)
        if self.transport_layer == "K":
            self.server.socket.settimeout(10)

        while True:
            self.handshake()
            if self.transport_layer == "U":
                time.sleep(1)
                self.server.socket.settimeout(self.server.timeout*4)

            time.sleep(0.5)

            self.read_data()
            if self.transport_layer == "T":
                self.server.close()
                exit(1)

            
           