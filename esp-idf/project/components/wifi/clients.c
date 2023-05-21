#include "wifi.h"

/* *****************************************************************************
 *                                                                             *
 *  ***********************    Handshake   ***************************    *
 *                                                                             *
 *  *************** <><><><><><><><><><><><><><><><><><><><> *************    *
 *                                                                             *
 *****************************************************************************/


int handshake(config_t *config, char restart, uint16_t device_id) {
    // Socket craetion
    struct sockaddr_in dest_addr;
    int err = -1;
    inet_pton(AF_INET, HOST_IP_ADDR, &dest_addr.sin_addr);
    dest_addr.sin_family = AF_INET;
    dest_addr.sin_port = htons(HANDSHAKE_PORT);
    int sock = socket(AF_INET, SOCK_STREAM, IPPROTO_IP);

    if (sock < 0) {
        ESP_LOGE(TAG, "Unable to create socket: errno %s\n", strerror(errno));
        return err;
    }

    ESP_LOGI(TAG, "Handshake Socket created, connecting to %s:%d", HOST_IP_ADDR,
             HANDSHAKE_PORT);

    err = connect(sock, (struct sockaddr *)&dest_addr, sizeof(dest_addr));
    if (err != 0) {
        ESP_LOGE(TAG, "Handshake Socket unable to connect: errno %s\n",
                 strerror(errno));
        return err;
    }
    ESP_LOGI(TAG, "Successfully connected Handshake Socket");

    // Send handshake initiation
    char buf_to_send[1024];
    const char *handshake_init = "hb";
    int offset = 0;
    memcpy(buf_to_send, handshake_init, strlen(handshake_init));
    offset += strlen(handshake_init);
    buf_to_send[strlen(handshake_init)] = restart;
    offset += 1;
    memcpy(buf_to_send + offset, &DEVICE_ID, sizeof(uint16_t));
    offset += sizeof(uint16_t);
    memcpy(buf_to_send + offset, &CUSTOM_GLOBAL_EPOCH_MICROSECONDS,
           sizeof(uint64_t));
    offset += sizeof(uint64_t);
    err = send(sock, buf_to_send, offset, 0);
    if (err < 0) {
        ESP_LOGE(TAG, "Error occurred during sending: errno %s\n",
                 strerror(errno));
        return err;
    }
    ESP_LOGI(TAG, "Handshake initiation sent");
    // Receive data back
    char rx_buffer[128];
    int len = recv(sock, rx_buffer, sizeof(rx_buffer) - 1, 0);

    // Error occurred during receiving
    if (len < 0) {
        ESP_LOGE(TAG, "recv failed: errno %s\n", strerror(errno));
        return err;
    }
    config->trans_layer = rx_buffer[0];
    config->protocol_id = ((int)rx_buffer[1]) - 48;
    ESP_LOGI(TAG, "bro sent me balues trans_layer %c protocol_id %d\n",
             config->trans_layer, (int)config->protocol_id);
    // Data received
    char *ok_bro = "ob";  // Conclude handshake
    err = send(sock, ok_bro, strlen(ok_bro), 0);
    if (err < 0) {
        ESP_LOGE(TAG, "Error occurred during sending: errno %s\n",
                 strerror(errno));
        return err;
    }
    ESP_LOGI(TAG, "HandshakeConcluded");
    close(sock);
    return 0;
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
    char *buffer = create_packet(protocol_id, &size_to_send,'T');
    if (buffer == NULL) return -1;
    ESP_LOGI(TAG, "Sending packet of size %d", size_to_send);
    int err = send_chunks_tcp(sock, buffer, 1024, size_to_send);

    free(buffer);
    ESP_LOGI(TAG, "Packe Sent!");
    return err;
}
void tcp_client(int protocol_id) {
    ESP_LOGI(TAG, "TCP Client Started");

    // Define ADDRESS
    struct sockaddr_in dest_addr;
    inet_pton(AF_INET, HOST_IP_ADDR, &dest_addr.sin_addr);
    dest_addr.sin_family = AF_INET;
    dest_addr.sin_port = htons(TCP_PORT);

    // Create socket
    int sock = socket(AF_INET, SOCK_STREAM, IPPROTO_IP);
    if (sock < 0) {
        ESP_LOGE(TAG, "Unable to create socket: errno %s\n", strerror(errno));
        return;
    }
    ESP_LOGI(TAG, "Socket created, connecting to %s:%d", HOST_IP_ADDR,
             TCP_PORT);

    // Connect to server
    int err = connect(sock, (struct sockaddr *)&dest_addr, sizeof(dest_addr));
    if (err != 0) {
        ESP_LOGE(TAG, "Socket unable to connect: errno %s\n", strerror(errno));
        return;
    }
    ESP_LOGI(TAG, "Successfully connected");

    // Send packets to server
    while (1) {
        err = send_pakcet_tcp(sock, protocol_id);
        if (err < 0) {
            ESP_LOGE(TAG, "Error occurred during sending: errno %s\n",
                     strerror(errno));
            break;
        }

        vTaskDelay(pdMS_TO_TICKS(60000));  // Sleep for 60 seconds
    }

    // Clean up socket
    if (sock != -1) {
        ESP_LOGE(TAG, "Shutting down socket and restarting...");
        shutdown(sock, 0);
        close(sock);
    }
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
    char *buffer = create_packet(protocol_id, &size_to_send,'U');
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

void udp_client(int protocol_id) {
    // char rx_buffer[1024];
    ESP_LOGI(TAG, "UDP Client Started ON %d", UDP_PORT);
    // Define ADDRESS
    struct sockaddr_in dest_addr;
    inet_pton(AF_INET, HOST_IP_ADDR, &dest_addr.sin_addr);
    dest_addr.sin_family = AF_INET;
    dest_addr.sin_port = htons(UDP_PORT);
    dest_addr.sin_addr.s_addr = inet_addr(HOST_IP_ADDR);
    // Create socket
    int sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_IP);

    if (sock < 0) {
        ESP_LOGE(TAG, "Unable to create socket: errno %s\n", strerror(errno));
        return;
    }

    ESP_LOGI(TAG, "Socket created, sending to %s:%d", HOST_IP_ADDR, UDP_PORT);

    ESP_LOGI(TAG, "Successfully connected");

    // Send and Recevie message to and from server
    while (1) {
        vTaskDelay(pdMS_TO_TICKS(UDP_TIMEOUT));  // delay for 1 seconds
        int err = send_pakcet_udp(sock, &dest_addr, protocol_id);
        // int err = send(sock, payload, strlen(payload), 0);
        if (err < 0) {
            ESP_LOGE(TAG, "Error occurred during sending: errno %s\n",
                     strerror(errno));
            break;
        }
    }

    if (sock != -1) {
        ESP_LOGE(TAG, "Shutting down socket and restarting...");
        shutdown(sock, 0);
        close(sock);
    }
}

/* *****************************************************************************
 *                                                                             *
 *  ***********************    MAIN FUN    ***************************    *
 *                                                                             *
 *  *************** <><><><><><><><><><><><><><><><><><><><> *************    *
 *                                                                             *
 *****************************************************************************/


void main_wifi(void) {
    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());
    ESP_ERROR_CHECK(example_connect());

    char restart = '0';

    ESP_LOGI(TAG, "\n\nDevice ID: %d!\n\n", DEVICE_ID);

    while (1) {
        config_t config;
        init_global_vars();
        handshake(&config, restart, DEVICE_ID);
        restart = '1';
        if (config.trans_layer == 'U') {
            udp_client(config.protocol_id);
        } else {
            tcp_client(config.protocol_id);
        }
    }
}