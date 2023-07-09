#include "wifi.h"

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
        // vtaskdelay
        ESP_LOGI(TAG, "Sent %d bytes of %d", bytes_sent, total);
    }

    return bytes_sent;  // Total bytes sent
}

int send_pakcet_tcp(int sock, int protocol_id) {
    int size_to_send = 0;
    char *first_buffer = create_packet(1, &size_to_send, 'T');

    if (first_buffer == NULL) return -1;

    int err = send_chunks_tcp(sock, first_buffer, 1024, size_to_send);
    free(first_buffer);
    // get response
    char *rx_buffer = (char *)malloc(1024);
    int len = recv(sock, rx_buffer, 1024 - 1, 0);

    // Error occurred during receiving
    if (len < 0) {
        ESP_LOGE(TAG, "recv failed: errno %s\n", strerror(errno));
        free(rx_buffer);
        return err;
    }

    // parse config
    config_t config;
    parse_config(rx_buffer, &config);
    // store config
    set_nvs_config(config);
    free(rx_buffer);

    char *buffer = create_packet(protocol_id, &size_to_send, 'T');
    if (buffer == NULL) return -1;
    ESP_LOGI(TAG, "Sending packet of size %d", size_to_send);
    err = send_chunks_tcp(sock, buffer, 1024, size_to_send);

    free(buffer);
    ESP_LOGI(TAG, "Packe Sent!");
    return err;
}
void tcp_client(int protocol_id) {
    config_t current_config;
    get_nvs_config(&current_config);

    ESP_LOGI(TAG, "TCP Client Started");

    // Define ADDRESS
    struct sockaddr_in dest_addr;
    inet_pton(AF_INET, current_config.host_ip_addr, &dest_addr.sin_addr);
    dest_addr.sin_family = AF_INET;
    dest_addr.sin_port = htons(current_config.tcp_port);

    // Create socket
    int sock = socket(AF_INET, SOCK_STREAM, IPPROTO_IP);

    if (sock < 0) {
        ESP_LOGE(TAG, "Unable to create socket: errno %s\n", strerror(errno));
        return;
    }
    ESP_LOGI(TAG, "Socket created, connecting to %s:%d",
             current_config.host_ip_addr, current_config.tcp_port);

    // Connect to server
    int err = connect(sock, (struct sockaddr *)&dest_addr, sizeof(dest_addr));
    if (err != 0) {
        ESP_LOGE(TAG, "Socket unable to connect: errno %s\n", strerror(errno));
        return;
    }
    ESP_LOGI(TAG, "Successfully connected");

    // Send packets to server
    while (1) {
        if (current_config.trans_layer == 'K'){
            vTaskDelay(pdMS_TO_TICKS(4000));
        }
        err = send_pakcet_tcp(sock, protocol_id);
        if (err < 0) {
            ESP_LOGE(TAG, "Error occurred during sending: errno %s\n",
                     strerror(errno));
            break;
        }
        if (current_config.trans_layer == 'T') {
            ESP_LOGI(TAG, "Going to sleep");
            esp_sleep_enable_timer_wakeup(
                (long long)(current_config.discontinuous_time * 60 * 1e+6));
            esp_deep_sleep_start();
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
 *  ***********************    UDP    ***************************    *
 *                                                                             *
 *  *************** <><><><><><><><><><><><><><><><><><><><> *************    *
 *                                                                             *
 *****************************************************************************/

int send_chunks_udp(int sock, const char *buf, int size, int total,
                    struct sockaddr_in *addr) {
    if (size <= 0) {
        return -1;  
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
            return ret;  
        }
        bytes_sent += ret;
    }

    return bytes_sent;  
}

int send_pakcet_udp(int sock, struct sockaddr_in *in_addr, int protocol_id) {
    int size_to_send = 0;
    struct sockaddr_in addr;
    socklen_t addr_len = sizeof(addr);
    char *first_buffer = create_packet(1, &size_to_send, 'U');
    if (first_buffer == NULL) return -1;
    ESP_LOGI(TAG, "Sending packet of size %d", size_to_send);
    int err = send_chunks_udp(sock, first_buffer, 1024, size_to_send, in_addr);
    free(first_buffer);
    char *rx_buffer = (char *)malloc(1024);
    ESP_LOGI(TAG, "Waiting for CONFIG");
    struct timeval timeout;
    timeout.tv_sec = 6;
    timeout.tv_usec = 0;

    if (setsockopt(sock, SOL_SOCKET, SO_RCVTIMEO, (char *)&timeout,
                   sizeof(timeout)) < 0) {
        ESP_LOGE(TAG, "setsockopt failed");
    }

    ESP_LOGI(TAG, "Waiting for CONFIG");
    int len =
        recvfrom(sock, rx_buffer, 1024, 0, (struct sockaddr *)&addr, &addr_len);

    if (len < 0) {
        ESP_LOGE(TAG, "recvfrom failed: errno %s\n", strerror(errno));
        free(rx_buffer);
        return -1;
    }
    ESP_LOGI(TAG, "Received %d bytes from %s:", len, inet_ntoa(addr.sin_addr));

    config_t config;
    parse_config(rx_buffer, &config);

    set_nvs_config(config);
    free(rx_buffer);
    ESP_LOGI(TAG, "CONFIG Received, SENDING PACKET OF PROTOCOL %d",
             protocol_id);
    char *buffer = create_packet(protocol_id, &size_to_send, 'U');
    if (buffer == NULL) return -1;
    ESP_LOGI(TAG, "Sending packet of size %d", size_to_send);
    ESP_LOGI(TAG, "Sending to %s:%d", inet_ntoa(in_addr->sin_addr),
             ntohs(in_addr->sin_port));
    err = send_chunks_udp(sock, buffer, 1024, size_to_send, in_addr);
    free(buffer);
    ESP_LOGI(TAG, "Packee Sen? %d", err);
    return err;
}

void udp_client(int protocol_id) {
    config_t current_config;
    get_nvs_config(&current_config);

    struct sockaddr_in dest_addr;
    inet_pton(AF_INET, current_config.host_ip_addr, &dest_addr.sin_addr);
    dest_addr.sin_family = AF_INET;
    dest_addr.sin_port = htons(current_config.udp_port);
    dest_addr.sin_addr.s_addr = inet_addr(current_config.host_ip_addr);
    int sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_IP);

    if (sock < 0) {
        ESP_LOGE(TAG, "Unable to create socket: errno %s\n", strerror(errno));
        return;
    }

    ESP_LOGI(TAG, "Socket created, sending to %s:%d",
             current_config.host_ip_addr, current_config.udp_port);

    ESP_LOGI(TAG, "Successfully connected");

    while (1) {
        vTaskDelay(pdMS_TO_TICKS(4000));  
        int err = send_pakcet_udp(sock, &dest_addr, protocol_id);
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

    ESP_LOGI(TAG, "\n\nDevice ID: %d!\n\n", DEVICE_ID);

    while (1) {
        init_global_vars();
        vTaskDelay(pdMS_TO_TICKS(6000));
        config_t config;
        get_nvs_config(&config);

        if (config.trans_layer == 'T' || config.trans_layer == 'K') {
            tcp_client(config.protocol_id);
        } else {
            udp_client(config.protocol_id);
        }
    }
}