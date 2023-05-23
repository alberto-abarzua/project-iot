import datetime
import os
import socket
import sys
import threading

from utils.exceptions import LossException
from utils.models import Data, DatabaseManager, Logs, Loss
from utils.packet_parser import PacketParser

TIMEOUT_TOLERANCE = 10


class HandShakeServer:

    def start_handshake(self):
        success = False
        SESP_PORT_HANDSHAKE = os.environ.get("SESP_PORT_HANDSHAKE")
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(("0.0.0.0", int(SESP_PORT_HANDSHAKE)))
        server_socket.listen(5)

        client_socket, client_address = server_socket.accept()
        print("Starting handshake")
        # wait for "helo bro"
        data = client_socket.recv(1024)
        if b"hb" in data:
            id_device = data[3:5]
            custom_epoch = data[5: 5 + 8]
            # convert to int
            id_device = int.from_bytes(id_device, byteorder="little")
            custom_epoch_millis = int.from_bytes(custom_epoch, byteorder="little")
            print("Handshake received from device", id_device,
                  "custom epoch", custom_epoch_millis)

            seconds, milliseconds = divmod(custom_epoch_millis, 1000)
            custom_epoch = datetime.datetime.utcfromtimestamp(
                seconds).replace(tzinfo=datetime.timezone.utc)
            custom_epoch = custom_epoch.replace(microsecond=milliseconds * 1000)
            # When not using sntp:
            print("custom_epcho, time", custom_epoch.timestamp())
            custom_epoch = datetime.datetime.utcnow().timestamp() - custom_epoch.timestamp()
            print("debug", custom_epoch, "utcnow", datetime.datetime.utcnow())

            config = DatabaseManager.get_default_config()
            config.last_access = datetime.datetime.utcnow()
            config.save()
            to_send_text = config.transport_layer + str(config.id_protocol)
            to_send_bytes = to_send_text.encode("utf-8")
            print("Sending config ...", to_send_bytes, len(to_send_bytes))
            client_socket.send(to_send_bytes)

        # wait for ok bro
        data = client_socket.recv(1024)
        if data == b"ob":
            print("Handshake successful!")
            # log
            print("Saving Log to db")
            log = Logs.create(
                timestamp=datetime.datetime.utcnow(),
                id_device=id_device,
                transport_layer=DatabaseManager.get_default_config().transport_layer,
                id_protocol=DatabaseManager.get_default_config().id_protocol,
                custom_epoch=custom_epoch,
            )
            log.save()
            success = True
        client_socket.shutdown(socket.SHUT_RDWR)
        server_socket.shutdown(socket.SHUT_RDWR)
        client_socket.close()
        server_socket.close()
        return success

    def run(self):
        while True:
            self.start_handshake()


# *****************************************************************************
# *                                                                           *
# *  ***********************    TCP    ***************************  *
# *                                                                           *
# *  *************** <><><><><><><><><><><><><><><><><><><><> *************  *
# *                                                                           *
# *****************************************************************************

class TcpServer:
    def recv_in_chunks(self, socket, total, chunk_size=1024):
        data = b""
        while len(data) < total:
            try:
                chunk = socket.recv(chunk_size)
            except TimeoutError:
                print("Timeout error, packets lost ...")
                raise LossException(total - len(data))
            if not chunk:
                break
            data += chunk
        return data

    def recv_headers(self, socket):
        try:
            headers = socket.recv(12)
            return headers
        except TimeoutError:
            print("Timeout error, packets lost ...")
            raise LossException(12)

    def run(self):
        start_time = datetime.datetime.utcnow()
        # copy of configs
        start_config = DatabaseManager.get_default_config()
        start_layer = start_config.transport_layer
        start_protocol = start_config.id_protocol

        print("Starting TCP server", start_config)
        # config as dict
        SESP_PORT_TCP = os.environ.get("SESP_PORT_TCP")
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(("0.0.0.0", int(SESP_PORT_TCP)))
        server_socket.listen(5)
        print("Server is listening on port: ", SESP_PORT_TCP)
        while True:
            client_socket, client_address = server_socket.accept()
            client_socket.settimeout(
                (int(os.environ.get("SESP_TCP_TIMEOUT")) // 1000) + TIMEOUT_TOLERANCE
            )
            print("Connection from: ", client_address)
            parser = PacketParser()
            while True:
                cur_config = DatabaseManager.get_default_config()
                recently_accesed = cur_config.was_recently_accessed(start_time)
                changed = cur_config.was_changed(start_layer, start_protocol)
                if recently_accesed or changed:
                    print("recently_accesed", recently_accesed, "changed", changed)
                    client_socket.shutdown(socket.SHUT_RDWR)
                    server_socket.shutdown(socket.SHUT_RDWR)
                    client_socket.close()
                    server_socket.close()
                    print("Config was recently accessed")
                    exit(1)
                try:
                    data_headers = self.recv_headers(client_socket)
                    headers = parser.parse_headers(data_headers)
                    _, _, _, id_protocol, message_length = headers
                    body = parser.parse_body(
                        self.recv_in_chunks(client_socket, message_length), id_protocol
                    )
                    DatabaseManager.save_to_db(headers, body)
                    print("Data saved to db")
                except LossException as e:
                    print("Loss exception!!!!")
                    bytes_lost = e.bytes_lost
                    Loss.create(
                        data=None,
                        bytes_lost=bytes_lost,
                        latency=0,
                    ).save()

                    client_socket.shutdown(socket.SHUT_RDWR)
                    server_socket.shutdown(socket.SHUT_RDWR)
                    client_socket.close()
                    server_socket.close()
                    exit(1)


# *****************************************************************************
# *                                                                           *
# *  ***********************    UDP    ***************************  *
# *                                                                           *
# *  *************** <><><><><><><><><><><><><><><><><><><><> *************  *
# *                                                                           *
# *****************************************************************************


class UdpServer:
    def recv_headers(self,socket):
        try:
            headers, _ = socket.recvfrom(12)
        except TimeoutError:
            print("Timeout error, packets lost ...")
            raise LossException(12)
        return headers


    def recv_in_chunks(self,socket, total, chunk_size=1024):
        data = b""
        while len(data) < total:
            chunk_size = min(chunk_size, total - len(data))
            try:
                chunk, _ = socket.recvfrom(chunk_size)
            except TimeoutError:
                print("Timeout error, packets lost ...")
                raise LossException(total - len(data))
            if not chunk:
                break
            data += chunk
        return data


    def run(self):
        start_time = datetime.datetime.utcnow()
        # copy of config
        start_config = DatabaseManager.get_default_config()
        start_layer = start_config.transport_layer
        start_protocol = start_config.id_protocol

        print("Starting udp server", start_config)
        # config as dict
        SESP_PORT_UDP = os.environ.get("SESP_PORT_UDP")
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(("0.0.0.0", int(SESP_PORT_UDP)))
        server_socket.settimeout(
            int(os.environ.get("SESP_UDP_TIMEOUT")) // 1000 + TIMEOUT_TOLERANCE
        )
        print("Server is listening on port: ", SESP_PORT_UDP)
        while True:
            parser = PacketParser()
            while True:
                cur_config = DatabaseManager.get_default_config()
                recently_accesed = cur_config.was_recently_accessed(start_time)
                changed = cur_config.was_changed(start_layer, start_protocol)
                if recently_accesed or changed:
                    print("recently_accesed", recently_accesed, "changed", changed)
                    print("Config was recently accessed")
                    exit(1)
                try:
                    data_headers = self.recv_headers(server_socket)
                    headers = parser.parse_headers(data_headers)
                    _, _, _, id_protocol, message_length = headers
                    body = parser.parse_body(
                        self.recv_in_chunks(server_socket, message_length), id_protocol
                    )
                    DatabaseManager.save_to_db(headers, body)
                    print("Data saved to db")
                except LossException as e:
                    print("Loss exception!!!!")
                    bytes_lost = e.bytes_lost
                    Loss.create(
                        data=None,
                        bytes_lost=bytes_lost,
                        latency=0,
                    ).save()
                    server_socket.shutdown(socket.SHUT_RDWR)
                    server_socket.close()
                    exit(1)


