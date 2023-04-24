from struct import unpack


class PacketParser:

    def __init__(self):
        return

    def parse_headers(self, byte_message: bytearray):
        """

        Parse the headers of the packet

            2 bytes id_devide , 6 bytes MAC, 1 Byte transport_layer , 1 Byte id_protocol , 2 bytes message_length
        """

        return unpack('<H6sbbH', byte_message)

    def parse_protocol_0(self, byte_message: bytearray):
        """
        Parse the message of the packet
                1,1,4 (bytes)
        """
        # last four bytes as int 
        print(len(byte_message))
        return unpack("<bbi", byte_message)

    def parse_protocol_1(self, byte_message: bytearray):
        """
        Parse the message of the packet
                1,1,4,1,4,1,4 (bytes)
        """
        return unpack("<bbibibi", byte_message)

    def parse_protocol_2(self, byte_message: bytearray):
        """
        Parse the message of the packet
                1,1,4,1,4,1,4,4 (bytes)
        """
        return unpack("<bbibibii", byte_message)

    def parse_protocol_3(self, byte_message: bytearray):
        """
        Parse the message of the packet
                1,1,4,1,4,1,4,4,4,4,4,4,4,4 (bytes)
        """
        return unpack("<bbibibiiiiiiii", byte_message)

    def parse_protocol_4(self, byte_message: bytearray):
        """
        Parse the message of the packet 

                1,1,4,1,4,1,4,8000,8000,8000 (bytes)
        """
        return unpack("<bbibibi8000s8000s8000s", byte_message)

    def parse_body(self, byte_message, id_protocol):
        msg_parser_dict = {
            0: self.parse_protocol_0,
            1: self.parse_protocol_1,
            2: self.parse_protocol_2,
            3: self.parse_protocol_3,
            4: self.parse_protocol_4,

        }
        parser = msg_parser_dict.get(int(id_protocol))
        if parser:
            return parser(byte_message)
