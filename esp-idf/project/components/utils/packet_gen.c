#include "utils.h"

hd_12345_t create_headers(char transport_layer, char protocol_id,
                          uint16_t msg_len) {
    hd_12345_t header = {
        DEVICE_ID,
        {DEVICE_MAC_ADDRESS[0], DEVICE_MAC_ADDRESS[1], DEVICE_MAC_ADDRESS[2],
         DEVICE_MAC_ADDRESS[3], DEVICE_MAC_ADDRESS[4], DEVICE_MAC_ADDRESS[5]},
        transport_layer,
        protocol_id,
        msg_len};
    return header;
}

char *create_packet_protocol1(int *a_packet_size, char transport_layer) {
    int packet_size = 1 * sizeof(char) + 1 * sizeof(int32_t);
    *a_packet_size = packet_size + sizeof(hd_12345_t);
    hd_12345_t header = create_headers(transport_layer, 1, packet_size);
    ds_p1234_t packet;
    packet.data1 = batt_level();
    packet.data2 = get_timestamp_from_custom_epoch();

    char *buffer = (char *)malloc(*a_packet_size);
    memcpy(buffer, &header, sizeof(hd_12345_t));
    memcpy(buffer + sizeof(hd_12345_t), &packet, packet_size);
    return buffer;
}

char *create_packet_protocol2(int *a_packet_size, char transport_layer) {
    int packet_size = 3 * sizeof(char) + 3 * sizeof(int32_t);
    *a_packet_size = packet_size + sizeof(hd_12345_t);
    hd_12345_t header = create_headers(transport_layer, 2, packet_size);
    ds_p1234_t packet;

    packet.data1 = batt_level();
    packet.data2 = get_timestamp_from_custom_epoch();
    packet.data3 = temp();
    packet.data4 = press();
    packet.data5 = hum();
    packet.data6 = co();

    char *buffer = (char *)malloc(*a_packet_size);
    memcpy(buffer, &header, sizeof(hd_12345_t));
    memcpy(buffer + sizeof(hd_12345_t), &packet, packet_size);
    return buffer;
}

char *create_packet_protocol3(int *a_packet_size, char transport_layer) {
    int packet_size = 3 * sizeof(char) + 4 * sizeof(int32_t);
    *a_packet_size = packet_size + sizeof(hd_12345_t);
    hd_12345_t header = create_headers(transport_layer, 3, packet_size);
    ds_p1234_t packet;
    packet.data1 = batt_level();
    packet.data2 = get_timestamp_from_custom_epoch();
    packet.data3 = temp();
    packet.data4 = press();
    packet.data5 = hum();
    packet.data6 = co();
    packet.data7 = rms();

    char *buffer = (char *)malloc(*a_packet_size);
    memcpy(buffer, &header, sizeof(hd_12345_t));
    memcpy(buffer + sizeof(hd_12345_t), &packet, packet_size);
    return buffer;
}

char *create_packet_protocol4(int *a_packet_size, char transport_layer) {
    int packet_size = 3 * sizeof(char) + 10 * sizeof(int32_t);
    *a_packet_size = packet_size + sizeof(hd_12345_t);

    hd_12345_t header = create_headers(transport_layer, 4, packet_size);
    ds_p1234_t packet;
    packet.data1 = batt_level();
    packet.data2 = get_timestamp_from_custom_epoch();
    packet.data3 = temp();
    packet.data4 = press();
    packet.data5 = hum();
    packet.data6 = co();
    packet.data7 = rms();
    packet.data8 = ampx();
    packet.data9 = freqx();
    packet.data10 = ampy();
    packet.data11 = freqy();
    packet.data12 = ampz();
    packet.data13 = freqz();

    char *buffer = (char *)malloc(*a_packet_size);
    memcpy(buffer, &header, sizeof(hd_12345_t));
    memcpy(buffer + sizeof(hd_12345_t), &packet, packet_size);
    return buffer;
}

char *create_packet_protocol5(int *a_packet_size, char transport_layer) {
    int base_packet_size = 3 * sizeof(char) + 3 * sizeof(int32_t);
    *a_packet_size = base_packet_size + sizeof(hd_12345_t) + 6 * 2000*sizeof(float);
    hd_12345_t header = create_headers(transport_layer, 5, *a_packet_size - sizeof(hd_12345_t));
    ds_p5_t packet;
    packet.data1 = batt_level();
    packet.data2 = get_timestamp_from_custom_epoch();
    packet.data3 = temp();
    packet.data4 = press();
    packet.data5 = hum();
    packet.data6 = co();
    char *buffer = (char *)malloc(*a_packet_size);
    memcpy(buffer, &header, sizeof(hd_12345_t));
    memcpy(buffer + sizeof(hd_12345_t), &packet, base_packet_size);
    int offset = sizeof(hd_12345_t) + base_packet_size;
    packet.data7 = buffer + offset;
    offset += 2000*sizeof(float);
    packet.data8 = buffer + offset;
    offset += 2000*sizeof(float);
    packet.data9 = buffer + offset;
    offset += 2000*sizeof(float);
    packet.data10 = buffer + offset;
    offset += 2000*sizeof(float);
    packet.data11 = buffer + offset;
    offset += 2000*sizeof(float);
    packet.data12 = buffer + offset;

    random_between_array(-16,16,packet.data7);
    random_between_array(-16,16,packet.data8);
    random_between_array(-16,16,packet.data9);

    random_between_array(-1000,1000,packet.data10);
    random_between_array(-1000,1000,packet.data11);
    random_between_array(-1000,1000,packet.data12);


    return buffer;
}

char *create_packet(int protocol_id, int *packet_size, char transport_layer) {
    switch (protocol_id) {
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
        case 5:
            return create_packet_protocol5(packet_size, transport_layer);
        default:
            return NULL;
            break;
        
    }
}
