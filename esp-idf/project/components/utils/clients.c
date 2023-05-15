#include "utils.h"

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
    memcpy(buf_to_send + offset, &device_id, sizeof(uint16_t));
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
    ESP_LOGI(TAG, "Socket created, connecting to %s:%d", HOST_IP_ADDR, TCP_PORT);

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
            ESP_LOGE(TAG, "Error occurred during sending: errno %s\n", strerror(errno));
            break;
        }

        vTaskDelay(pdMS_TO_TICKS(60000)); // Sleep for 60 seconds
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
