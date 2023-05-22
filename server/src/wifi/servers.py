import datetime
import os
import socket
import sys
import threading

from utils.exceptions import LossException
from utils.models import Data, Logs, Loss,DatabaseManager
from utils.packet_parser import PacketParser


TIMEOUT_TOLERANCE = 10


def handshake_server():
    while True:
        start_handshake()


def start_handshake():
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
        print("Handshake received from device", id_device, "custom epoch", custom_epoch_millis)

        seconds, milliseconds = divmod(custom_epoch_millis, 1000)
        custom_epoch = datetime.datetime.utcfromtimestamp(seconds)
        custom_epoch = custom_epoch.replace(microsecond=milliseconds * 1000)
        # When not using sntp:
        custom_epoch = datetime.datetime.now().timestamp() - custom_epoch.timestamp()
        
        config = DatabaseManager().get_default_config()
        config.last_access = datetime.datetime.now()
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
            timestamp=datetime.datetime.now(),
            id_device=id_device,
            transport_layer=get_default_config().transport_layer,
            id_protocol=get_default_config().id_protocol,
            custom_epoch=custom_epoch,
        )
        log.save()
        success = True
    client_socket.shutdown(socket.SHUT_RDWR)
    server_socket.shutdown(socket.SHUT_RDWR)
    client_socket.close()
    server_socket.close()
    return success


def save_to_db(headers, body):
    new_entry = Data.create()
    custom_epoch = DatabaseManager().get_last_log().custom_epoch
    id_device, mac, transport_layer, id_protocol, message_length = headers
    val, batt_level, timestamp = body[:3]
    new_entry.id_device = id_device
    new_entry.mac = mac
    new_entry.transport_layer = transport_layer
    new_entry.id_protocol = id_protocol
    new_entry.message_length = message_length
    new_entry.val = val
    new_entry.batt_level = batt_level
    timestamp += custom_epoch.timestamp() * 1000
    seconds, milliseconds = divmod(timestamp, 1000)
    timestamp = datetime.datetime.utcfromtimestamp(seconds)
    timestamp = timestamp.replace(microsecond=int(milliseconds) * 1000)
    # add custom epoch (mili seconds)
    new_entry.timestamp = timestamp
    if id_protocol >= 1:
        temp, press, hum, Co = body[3: 3 + 4]
        new_entry.temp = temp
        new_entry.press = press
        new_entry.hum = hum
        new_entry.Co = Co
        if id_protocol == 2 or id_protocol == 3:
            RMS = body[7]
            new_entry.RMS = RMS
            if id_protocol == 3:
                AMP_X, FREQ_X, AMP_Y, FREQ_Y, AMP_Z, FREQ_Z = body[8:14]
                new_entry.AMP_X = AMP_X
                new_entry.FREQ_X = FREQ_X
                new_entry.AMP_Y = AMP_Y
                new_entry.FREQ_Y = FREQ_Y
                new_entry.AMP_Z = AMP_Z
                new_entry.FREQ_Z = FREQ_Z
        else:
            ACC_X, ACC_Y, ACC_Z = body[7:]
            new_entry.ACC_X = ACC_X
            new_entry.ACC_Y = ACC_Y
            new_entry.ACC_Z = ACC_Z
    new_entry.save()
    timestamp_now = datetime.datetime.now().timestamp()
    dif_timestamp = timestamp_now - timestamp.timestamp()
    print(
        f"Timestamp now: {timestamp_now}  Timestamp esp {timestamp.timestamp()} \
        | Diff: {dif_timestamp}"
    )
    dif_in_miliseconds = int(dif_timestamp * 1000)
    Loss.get_or_create(data=new_entry, bytes_lost=0, latency=dif_in_miliseconds)


# *****************************************************************************
# *                                                                           *
# *  ***********************    TCP    ***************************  *
# *                                                                           *
# *  *************** <><><><><><><><><><><><><><><><><><><><> *************  *
# *                                                                           *
# *****************************************************************************


def recv_in_chunks_tcp(socket, total, chunk_size=1024):
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


def recv_headers_tcp(socket):
    try:
        headers = socket.recv(12)
        return headers
    except TimeoutError:
        print("Timeout error, packets lost ...")
        raise LossException(12)


def server_tcp():
    start_time = datetime.datetime.now()
    # copy of config
    start_config = get_default_config()
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
            (int(os.environ.get("SESP_TCP_TIMEOUT")) // 1000) + TIMEOUT_TOLERANCE)
        print("Connection from: ", client_address)
        parser = PacketParser()
        while True:
            cur_config = get_default_config()
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
                data_headers = recv_headers_tcp(client_socket)
                headers = parser.parse_headers(data_headers)
                _, _, _, id_protocol, message_length = headers
                body = parser.parse_body(
                    recv_in_chunks_tcp(client_socket, message_length), id_protocol
                )
                save_to_db(headers, body)
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


def recv_headers_udp(socket):
    try:
        headers, _ = socket.recvfrom(12)
    except TimeoutError:
        print("Timeout error, packets lost ...")
        raise LossException(12)
    return headers


def recv_in_chunks_udp(socket, total, chunk_size=1024):
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


def server_udp():
    start_time = datetime.datetime.now()
    # copy of config
    start_config = get_default_config()
    start_layer = start_config.transport_layer
    start_protocol = start_config.id_protocol

    print("Starting udp server", start_config)
    # config as dict
    SESP_PORT_UDP = os.environ.get("SESP_PORT_UDP")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("0.0.0.0", int(SESP_PORT_UDP)))
    server_socket.settimeout(int(os.environ.get("SESP_UDP_TIMEOUT")) // 1000 + TIMEOUT_TOLERANCE)
    print("Server is listening on port: ", SESP_PORT_UDP)
    while True:
        parser = PacketParser()
        while True:
            cur_config = get_default_config()
            recently_accesed = cur_config.was_recently_accessed(start_time)
            changed = cur_config.was_changed(start_layer, start_protocol)
            if recently_accesed or changed:
                print("recently_accesed", recently_accesed, "changed", changed)
                server_socket.shutdown(socket.SHUT_RDWR)
                server_socket.close()
                print("Config was recently accessed")
                exit(1)
            try:
                data_headers = recv_headers_udp(server_socket)
                headers = parser.parse_headers(data_headers)
                _, _, _, id_protocol, message_length = headers
                body = parser.parse_body(
                    recv_in_chunks_udp(server_socket, message_length), id_protocol
                )
                save_to_db(headers, body)
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


def run_server_on_thread(target_fun):
    original_stdout = sys.stdout

    def target_fun_with_redirected_stdout():
        sys.stdout = original_stdout
        try:
            target_fun()
        finally:
            sys.stdout = sys.__stdout__

    proc = threading.Thread(target=target_fun_with_redirected_stdout)
    proc.start()
    return proc
