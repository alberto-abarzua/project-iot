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
            1 Byte id_protocol , 2 bytes message_length
        """

        return unpack("<H6sbbH", byte_message)

    def parse_body(self, byte_message, id_protocol):
        self.format_strings = {
            0: "<bbi",
            1: "<bbibibi",
            2: "<bbibibii",
            3: "<bbibibiiiiiiii",
            4: "<bbibibi8000s8000s8000s",
        }
        fmt = self.format_strings.get(int(id_protocol))
        if fmt:
            required_size = struct.calcsize(fmt)
        else:
            required_size = None
        try:
            return unpack(self.format_strings[id_protocol], byte_message)
        except struct.error:
            raise LossException(required_size - len(byte_message))

        except Exception:
            if required_size:
                raise LossException(required_size - len(byte_message))
            else:
                raise LossException(12)

    def pack_config(self, config):
        protocol_id = int(config.id_protocol)
        transport_layer = ord(config.transport_layer)
        msg = b"con"
        msg += struct.pack("<bb", transport_layer,protocol_id )
        return msg
