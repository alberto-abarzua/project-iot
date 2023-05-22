#include "utils.h"

hd_01234_t create_headers(char transport_layer, char protocol_id,
                          uint16_t msg_len) {
    hd_01234_t header = {
        DEVICE_ID,
        {DEVICE_MAC_ADDRESS[0], DEVICE_MAC_ADDRESS[1], DEVICE_MAC_ADDRESS[2],
         DEVICE_MAC_ADDRESS[3], DEVICE_MAC_ADDRESS[4], DEVICE_MAC_ADDRESS[5]},
        transport_layer,
        protocol_id,
        msg_len};
    return header;
}

char *create_packet_protocol0(int *a_packet_size, char transport_layer) {
    int packet_size = 2 * sizeof(char) + 1 * sizeof(int32_t);
    *a_packet_size = packet_size + sizeof(hd_01234_t);
    hd_01234_t header = create_headers(transport_layer, 0, packet_size);
    ds_p0123_t packet;
    packet.data1 = val1();
    packet.data2 = batt_level();
    packet.data3 = get_timestamp_from_custom_epoch();

    char *buffer = (char *)malloc(*a_packet_size);
    memcpy(buffer, &header, sizeof(hd_01234_t));
    memcpy(buffer + sizeof(hd_01234_t), &packet, packet_size);
    return buffer;
}

char *create_packet_protocol1(int *a_packet_size, char transport_layer) {
    int packet_size = 4 * sizeof(char) + 3 * sizeof(int32_t);
    *a_packet_size = packet_size + sizeof(hd_01234_t);
    hd_01234_t header = create_headers(transport_layer, 1, packet_size);
    ds_p0123_t packet;

    packet.data1 = val1();
    packet.data2 = batt_level();
    packet.data3 = get_timestamp_from_custom_epoch();
    packet.data4 = temp();
    packet.data5 = press();
    packet.data6 = hum();
    packet.data7 = co();

    char *buffer = (char *)malloc(*a_packet_size);
    memcpy(buffer, &header, sizeof(hd_01234_t));
    memcpy(buffer + sizeof(hd_01234_t), &packet, packet_size);
    return buffer;
}

char *create_packet_protocol2(int *a_packet_size, char transport_layer) {
    int packet_size = 4 * sizeof(char) + 4 * sizeof(int32_t);
    *a_packet_size = packet_size + sizeof(hd_01234_t);
    hd_01234_t header = create_headers(transport_layer, 2, packet_size);
    ds_p0123_t packet;
    packet.data1 = val1();
    packet.data2 = batt_level();
    packet.data3 = get_timestamp_from_custom_epoch();
    packet.data4 = temp();
    packet.data5 = press();
    packet.data6 = hum();
    packet.data7 = co();
    packet.data8 = 2147483647;

    char *buffer = (char *)malloc(*a_packet_size);
    memcpy(buffer, &header, sizeof(hd_01234_t));
    memcpy(buffer + sizeof(hd_01234_t), &packet, packet_size);
    return buffer;
}

char *create_packet_protocol3(int *a_packet_size, char transport_layer) {
    int packet_size = 4 * sizeof(char) + 10 * sizeof(int32_t);
    *a_packet_size = packet_size + sizeof(hd_01234_t);

    hd_01234_t header = create_headers(transport_layer, 3, packet_size);
    ds_p0123_t packet;
    packet.data1 = val1();
    packet.data2 = batt_level();
    packet.data3 = get_timestamp_from_custom_epoch();
    packet.data4 = temp();
    packet.data5 = press();
    packet.data6 = hum();
    packet.data7 = co();
    packet.data8 = rms();
    packet.data9 = ampx();
    packet.data10 = freqx();
    packet.data11 = ampy();
    packet.data12 = freqy();
    packet.data13 = ampz();
    packet.data14 = freqz();

    char *buffer = (char *)malloc(*a_packet_size);
    memcpy(buffer, &header, sizeof(hd_01234_t));
    memcpy(buffer + sizeof(hd_01234_t), &packet, packet_size);
    return buffer;
}

char *create_packet_protocol4(int *a_packet_size, char transport_layer) {
    int base_packet_size = 4 * sizeof(char) + 3 * sizeof(int32_t);
    *a_packet_size = base_packet_size + sizeof(hd_01234_t) + 3 * 8000;
    hd_01234_t header = create_headers(transport_layer, 4, *a_packet_size - sizeof(hd_01234_t));
    ds_p4_t packet;
    packet.data1 = val1();
    packet.data2 = batt_level();
    packet.data3 = get_timestamp_from_custom_epoch();
    packet.data4 = temp();
    packet.data5 = press();
    packet.data6 = hum();
    packet.data7 = co();
    char *buffer = (char *)malloc(*a_packet_size);
    memcpy(buffer, &header, sizeof(hd_01234_t));
    memcpy(buffer + sizeof(hd_01234_t), &packet, base_packet_size);
    int offset = sizeof(hd_01234_t) + base_packet_size;
    packet.data8 = buffer + offset;
    offset += 8000;
    packet.data9 = buffer + offset;
    offset += 8000;
    packet.data10 = buffer + offset;

    accx(packet.data8);
    accy(packet.data9);
    accz(packet.data10);

    return buffer;
}

char *create_packet(int protocol_id, int *packet_size, char transport_layer) {
    switch (protocol_id) {
        case 0:
            return create_packet_protocol0(packet_size, transport_layer);
            break;
        case 1:
            return create_packet_protocol1(packet_size, transport_layer);
            break;
        case 2:
            return create_packet_protocol2(packet_size, transport_layer);
            break;
        case 3:
            return create_packet_protocol3(packet_size, transport_layer);
            break;
        case 4:
            return create_packet_protocol4(packet_size, transport_layer);
            break;
        default:
            return NULL;
            break;
    }
}
