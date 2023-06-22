import struct
from struct import unpack

from utils.exceptions import LossException
from utils.prints import console


class PacketParser:
    def __init__(self):
        return

    def parse_headers(self, byte_message: bytearray):
        """

        Parse the headers of the packet

            2 bytes id_devide , 6 bytes MAC, 1 Byte transport_layer ,
            1 Byte protocol_id , 2 bytes message_length
        """

        return unpack("<H6sbbH", byte_message)

    def parse_body(self, byte_message, protocol_id):
        self.format_strings = {
            1: "<bi",
            2: "<bibibi",
            3: "<bibibii",
            4: "<bibibiiiiiiii",
            5: "<bibibi2000s2000s2000s2000s2000s2000s",
        }
        fmt = self.format_strings.get(int(protocol_id))
        if fmt:
            required_size = struct.calcsize(fmt)
        else:
            required_size = None
        try:
            return unpack(self.format_strings[protocol_id], byte_message)
        except struct.error:
            raise LossException(required_size - len(byte_message))

        except Exception:
            if required_size:
                raise LossException(required_size - len(byte_message))
            else:
                raise LossException(12)

    def pack_config(self, config):
        # Original configuration values
        status = int(config.status)
        protocol_id = int(config.protocol_id)
        bmi270_sampling = int(config.bmi270_sampling)
        bmi270_sensibility = int(config.bmi270_sensibility)
        bmi270_gyro_sensibility = int(config.bmi270_gyro_sensibility)
        bme688_sampling = int(config.bme688_sampling)
        discontinuous_time = int(config.discontinuous_time)
        tcp_port = int(config.tcp_port)
        udp_port = int(config.udp_port)

        # Padded strings
        host_ip_addr = str(config.host_ip_addr).ljust(15, '\0').encode() # max length for an IP v4 address
        ssid = str(config.ssid).ljust(32, '\0').encode() # max length for an SSID
        password = str(config.password).ljust(64, '\0').encode() # arbitrary max length for a password

        # String lengths
        host_ip_addr_len = 15
        ssid_len = 32
        password_len = 64

        transport_layer = config.transport_layer.encode()

        con = b"con"
        data = struct.pack('<iiiiiiiiii15si32si64sc',
                            status, protocol_id, bmi270_sampling,
                            bmi270_sensibility, bmi270_gyro_sensibility, bme688_sampling,
                            discontinuous_time, tcp_port, udp_port,
                            host_ip_addr_len, host_ip_addr , ssid_len, ssid, password_len, password,
                            transport_layer)
        msg = con + data
        return msg
