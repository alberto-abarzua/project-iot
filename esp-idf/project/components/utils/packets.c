#include "utils.h"


char *create_packet_protocol0(int *a_packet_size) {
    int packet_size = 2 * sizeof(char) + 1 * sizeof(int32_t);
    *a_packet_size = packet_size + sizeof(hd_01234_t);
    hd_01234_t header = {(int16_t)23, "123456", 0, 0,
                         (int16_t)*a_packet_size - sizeof(hd_01234_t)};
    ds_p0123_t packet;
    packet.data1 = '1';
    packet.data2 = '1';
    packet.data3 = get_timestamp_from_custom_epoch();

    char *buffer = (char *)malloc(*a_packet_size);
    memcpy(buffer, &header, sizeof(hd_01234_t));
    memcpy(buffer + sizeof(hd_01234_t), &packet, packet_size);
    return buffer;
}

char *create_packet_protocol1(int *a_packet_size) {
    int packet_size = 4 * sizeof(char) + 3 * sizeof(int32_t);
    *a_packet_size = packet_size + sizeof(hd_01234_t);
    hd_01234_t header = {(int16_t)23, "123456", 0, 1,
                         (int16_t)*a_packet_size - sizeof(hd_01234_t)};
    ds_p0123_t packet;

    packet.data1 = '1';
    packet.data2 = '1';
    packet.data3 = get_timestamp_from_custom_epoch();
    packet.data4 = '1';
    packet.data5 = 2147483647;
    packet.data6 = '1';
    packet.data7 = 2147483647;

    char *buffer = (char *)malloc(*a_packet_size);
    memcpy(buffer, &header, sizeof(hd_01234_t));
    memcpy(buffer + sizeof(hd_01234_t), &packet, packet_size);
    return buffer;
}

char *create_packet_protocol2(int *a_packet_size) {
    int packet_size = 4 * sizeof(char) + 4 * sizeof(int32_t);
    *a_packet_size = packet_size + sizeof(hd_01234_t);
    hd_01234_t header = {(int16_t)23, "123456", 0, 2,
                         (int16_t)*a_packet_size - sizeof(hd_01234_t)};
    ds_p0123_t packet;
    packet.data1 = '1';
    packet.data2 = '1';
    packet.data3 = get_timestamp_from_custom_epoch();
    packet.data4 = '1';
    packet.data5 = 2147483647;
    packet.data6 = '1';
    packet.data7 = 2147483647;
    packet.data8 = 2147483647;

    char *buffer = (char *)malloc(*a_packet_size);
    memcpy(buffer, &header, sizeof(hd_01234_t));
    memcpy(buffer + sizeof(hd_01234_t), &packet, packet_size);
    return buffer;
}

char *create_packet_protocol3(int *a_packet_size) {
    int packet_size = 4 * sizeof(char) + 10 * sizeof(int32_t);
    *a_packet_size = packet_size + sizeof(hd_01234_t);

    hd_01234_t header = {(int16_t)23, "123456", 0, 3,
                         (int16_t)*a_packet_size - sizeof(hd_01234_t)};
    ds_p0123_t packet;
    packet.data1 = '1';
    packet.data2 = '1';
    packet.data3 = get_timestamp_from_custom_epoch();
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

    char *buffer = (char *)malloc(*a_packet_size);
    memcpy(buffer, &header, sizeof(hd_01234_t));
    memcpy(buffer + sizeof(hd_01234_t), &packet, packet_size);
    return buffer;
}

char *create_packet_protocol4(int *a_packet_size) {
    int base_packet_size = 4 * sizeof(char) + 3 * sizeof(int32_t);
    *a_packet_size = base_packet_size + sizeof(hd_01234_t) + 3 * 8000;
    hd_01234_t header = {(int16_t)23, "123456", 0, 4,
                         (int16_t)*a_packet_size - sizeof(hd_01234_t)};
    ds_p4_t packet;
    packet.data1 = '1';
    packet.data2 = '1';
    packet.data3 = get_timestamp_from_custom_epoch();
    packet.data4 = '1';
    packet.data5 = 2147483647;
    packet.data6 = '1';
    packet.data7 = 2147483647;
    char *buffer = (char *)malloc(*a_packet_size);
    memcpy(buffer, &header, sizeof(hd_01234_t));
    memcpy(buffer + sizeof(hd_01234_t), &packet, base_packet_size);
    int offset = sizeof(hd_01234_t) + base_packet_size;
    packet.data8 = buffer + offset;
    offset += 8000;
    packet.data9 = buffer + offset;
    offset += 8000;
    packet.data10 = buffer + offset;

    memset(packet.data8, '1', 8000);

    memset(packet.data9, '1', 8000);

    memset(packet.data10, '1', 8000);

    return buffer;
}

char *create_packet(int protocol_id, int *packet_size) {
    switch (protocol_id) {
        case 0:
            return create_packet_protocol0(packet_size);
            break;
        case 1:
            return create_packet_protocol1(packet_size);
            break;
        case 2:
            return create_packet_protocol2(packet_size);
            break;
        case 3:
            return create_packet_protocol3(packet_size);
            break;
        case 4:
            return create_packet_protocol4(packet_size);
            break;
        default:
            return NULL;
            break;
    }
}

/* *****************************************************************************
 *                                                                             *
 *  ***********************    TCP   ***************************    *
 *                                                                             *
 *  *************** <><><><><><><><><><><><><><><><><><><><> *************    *
 *                                                                             *
 *****************************************************************************/

int send_chunks_tcp(int sock, const char *buf, int size, int total) {
    if (size <= 0) {
        return -1;  // Invalid chunk size
    }

    int bytes_sent = 0;
    while (bytes_sent < total) {
        int remaining_bytes = total - bytes_sent;
        int chunk_size = remaining_bytes < size ? remaining_bytes : size;
        const char *chunk_ptr = buf + bytes_sent;

        int sent = 0;
        while (sent < chunk_size) {
            int ret = send(sock, chunk_ptr + sent, chunk_size - sent, 0);
            if (ret < 0) {
                return ret;  // Send error
            }
            sent += ret;
        }
        bytes_sent += sent;
    }

    return bytes_sent;  // Total bytes sent
}

int send_pakcet_tcp(int sock, int protocol_id) {
    int size_to_send = 0;
    char *buffer = create_packet(protocol_id, &size_to_send);
    if (buffer == NULL) return -1;
    ESP_LOGI(TAG, "Sending packet of size %d", size_to_send);
    int err = send_chunks_tcp(sock, buffer, 1024, size_to_send);

    free(buffer);
    ESP_LOGI(TAG, "Packe Sent!");
    return err;
}

/* *****************************************************************************
 *                                                                             *
 *  ***********************    UDP    ***************************    *
 *                                                                             *
 *  *************** <><><><><><><><><><><><><><><><><><><><> *************    *
 *                                                                             *
 *****************************************************************************/

int send_chunks_udp(int sock, const char *buf, int size, int total,
                    struct sockaddr_in *addr) {
    if (size <= 0) {
        return -1;  // Invalid chunk size
    }
    int bytes_sent = 0;
    while (bytes_sent < total) {
        int remaining_bytes = total - bytes_sent;
        int chunk_size = remaining_bytes < size ? remaining_bytes : size;
        if (bytes_sent == 0) {
            chunk_size = 12;
        }
        const char *chunk_ptr = buf + bytes_sent;

        int ret = sendto(sock, chunk_ptr, chunk_size, 0,
                         (struct sockaddr *)addr, sizeof(*addr));
        if (ret < 0) {
            return ret;  // Send error
        }
        bytes_sent += ret;
    }

    return bytes_sent;  // Total bytes sent
}

int send_pakcet_udp(int sock, struct sockaddr_in *in_addr, int protocol_id) {
    int size_to_send = 0;
    char *buffer = create_packet(protocol_id, &size_to_send);
    if (buffer == NULL) return -1;
    ESP_LOGI(TAG, "Sending packet of size %d", size_to_send);
    // log address and port
    ESP_LOGI(TAG, "Sending to %s:%d", inet_ntoa(in_addr->sin_addr),
             ntohs(in_addr->sin_port));
    int err = send_chunks_udp(sock, buffer, 1024, size_to_send, in_addr);
    free(buffer);
    ESP_LOGI(TAG, "Packee Sen? %d", err);
    return err;
}