#include "utils.h"

void tcp_client(void) {
    // char rx_buffer[1024];
    ESP_LOGI(TAG, "TCP Client Started");

    while (1) {
        // Define ADDRESS
        struct sockaddr_in dest_addr;
        inet_pton(AF_INET, HOST_IP_ADDR, &dest_addr.sin_addr);
        dest_addr.sin_family = AF_INET;
        dest_addr.sin_port = htons(TCP_PORT);
        // Create socket
        int sock = socket(AF_INET, SOCK_STREAM, IPPROTO_IP);

        if (sock < 0) {
            ESP_LOGE(TAG, "Unable to create socket: errno %s\n",
                     strerror(errno));
            break;
        }

        ESP_LOGI(TAG, "Socket created, connecting to %s:%d", HOST_IP_ADDR,
                 TCP_PORT);

        int err =
            connect(sock, (struct sockaddr *)&dest_addr, sizeof(dest_addr));
        if (err != 0) {
            ESP_LOGE(TAG, "Socket unable to connect: errno %s\n",
                     strerror(errno));
            break;
        }
        ESP_LOGI(TAG, "Successfully connected");

        // Send and Recevie message to and from server
        while (1) {
            vTaskDelay(pdMS_TO_TICKS(1000));  // delay for 1 seconds
            int err = send_pakcet_tcp(sock, 4);
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
}

void udp_client(void) {
    // char rx_buffer[1024];
    ESP_LOGI(TAG, "UDP Client Started ON %d",UDP_PORT);
    while (1) {
        // Define ADDRESS
        struct sockaddr_in dest_addr;
        inet_pton(AF_INET, HOST_IP_ADDR, &dest_addr.sin_addr);
        dest_addr.sin_family = AF_INET;
        dest_addr.sin_port = htons(UDP_PORT);
        dest_addr.sin_addr.s_addr = inet_addr(HOST_IP_ADDR);
        // Create socket
        int sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_IP);

        if (sock < 0) {
            ESP_LOGE(TAG, "Unable to create socket: errno %s\n",
                     strerror(errno));
            break;
        }

        ESP_LOGI(TAG, "Socket created, sending to %s:%d", HOST_IP_ADDR,
                 UDP_PORT);

        ESP_LOGI(TAG, "Successfully connected");

        // Send and Recevie message to and from server
        while (1) {
            vTaskDelay(pdMS_TO_TICKS(1000));  // delay for 1 seconds
            int err = send_pakcet_udp(sock, &dest_addr, 0);
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
}
