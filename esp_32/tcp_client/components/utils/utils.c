#include "utils.h"

#include <sys/socket.h>

int pack(char *buffer, hd_01234_t *header, void *packet, int16_t limit_packet) {
    int32_t offset = 0;
    memcpy(buffer + offset, header, sizeof(hd_01234_t));
    offset += sizeof(hd_01234_t);
    memcpy(buffer + offset, packet, limit_packet);
    offset += limit_packet;
    return offset;
}

int send_packet_protocol0(int sock) {
    hd_01234_t header = {(int16_t)23, "123456", 0, 0, (int16_t)23};
    ds_p0123_t packet;
    packet.data1 = '1';
    packet.data2 = '1';
    packet.data3 = 2147483647;

    char buffer[1024];
    int16_t limit_packet = 2 * sizeof(char) + sizeof(int32_t);
    int16_t size_buffer = pack(buffer, &header, &packet, limit_packet);

    int err = send(sock, buffer, size_buffer, 0);
    return err;
}

int min(int a, int b) { return (a < b) ? a : b; }
int send_packet_protocol1(int sock) {
    hd_01234_t header = {(int16_t)23, "123456", 0, 1, (int16_t)23};
    ds_p0123_t packet;
    packet.data1 = '1';
    packet.data2 = '1';
    packet.data3 = 2147483647;
    packet.data4 = '1';
    packet.data5 = 2147483647;
    packet.data6 = '1';
    packet.data7 = 2147483647;

    char buffer[1024];
    int16_t limit_packet = 4 * sizeof(char) + 3 * sizeof(int32_t);
    int16_t size_buffer = pack(buffer, &header, &packet, limit_packet);

    int err = send(sock, buffer, size_buffer, 0);
    return err;
}

int send_packet_protocol2(int sock) {
    hd_01234_t header = {(int16_t)23, "123456", 0, 2, (int16_t)23};
    ds_p0123_t packet;
    packet.data1 = '1';
    packet.data2 = '1';
    packet.data3 = 2147483647;
    packet.data4 = '1';
    packet.data5 = 2147483647;
    packet.data6 = '1';
    packet.data7 = 2147483647;
    packet.data8 = 2147483647;

    char buffer[1024];
    int16_t limit_packet = 4 * sizeof(char) + 4 * sizeof(int32_t);
    int16_t size_buffer = pack(buffer, &header, &packet, limit_packet);

    int err = send(sock, buffer, size_buffer, 0);
    return err;
}

int send_packet_protocol3(int sock) {
    hd_01234_t header = {(int16_t)23, "123456", 0, 3, (int16_t)23};
    ds_p0123_t packet;
    packet.data1 = '1';
    packet.data2 = '1';
    packet.data3 = 2147483647;
    packet.data4 = '1';
    packet.data5 = 2147483647;
    packet.data6 = '1';
    packet.data7 = 2147483647;
    packet.data8 = 2147483647;
    packet.data9 = 2147483647;
    packet.data10 = 2147483647;
    packet.data11 = 2147483647;
    packet.data12 = 2147483647;
    packet.data13 = 2147483647;
    packet.data14 = 2147483647;

    char buffer[1024];
    int16_t limit_packet = 4 * sizeof(char) + 10 * sizeof(int32_t);
    int16_t size_buffer = pack(buffer, &header, &packet, limit_packet);

    int err = send(sock, buffer, size_buffer, 0);
    return err;
}

int send_big(int sock, char *buf, int size, int total) {
    int err = -1;
    for (int i = 0; i < total; i += size) {
        err = send(sock, buf + i, min(size, total - i), 0);
        if (err < 0) return err;
    }
    return err;
}

int send_packet_protocol4(int sock) {
    hd_01234_t header = {(int16_t)23, "123456", 0, 4, (int16_t)23};
    ds_p4_t packet;
    packet.data1 = '1';
    packet.data2 = '1';
    packet.data3 = 2147483647;
    packet.data4 = '1';
    packet.data5 = 2147483647;
    packet.data6 = '1';
    packet.data7 = 2147483647;

    packet.data8 = (char *)malloc(8000);
    memset(packet.data8, '1', 8000);

    packet.data9 = (char *)malloc(8000);
    memset(packet.data9, '1', 8000);

    packet.data10 = (char *)malloc(8000);
    memset(packet.data10, '1', 8000);

    char buffer[1024];
    int16_t limit_packet = 4 * sizeof(char) + 3 * sizeof(int32_t);
    int16_t size_buffer = pack(buffer, &header, &packet, limit_packet);
    int err = send(sock, buffer, size_buffer, 0);
    if (err < 0) return err;

    send_big(sock, packet.data8, 1000, 8000);
    send_big(sock, packet.data9, 1000, 8000);
    send_big(sock, packet.data10, 1000, 8000);

    free(packet.data8);
    free(packet.data9);
    free(packet.data10);
    return err;
}

int send_pakcet(int sock, int protocol_id) {
    switch (protocol_id) {
        case 0:
            return send_packet_protocol0(sock);
            break;
        case 1:
            return send_packet_protocol1(sock);
            break;
        case 2:
            return send_packet_protocol2(sock);
            break;
        case 3:
            return send_packet_protocol3(sock);
            break;
        case 4:
            return send_packet_protocol4(sock);
            break;
        default:
            return -1;
            break;
    }
}