#include "utils.h"

void tcp_client(void) {
    char rx_buffer[128];
    char host_ip[] = HOST_IP_ADDR;
    int addr_family = 0;
    int ip_protocol = 0;
    
    while (1) {
        //Define ADDRESS
        struct sockaddr_in dest_addr;
        inet_pton(AF_INET, host_ip, &dest_addr.sin_addr);
        dest_addr.sin_family = AF_INET;
        dest_addr.sin_port = htons(PORT);
        addr_family = AF_INET;
        ip_protocol = IPPROTO_IP;
        // Create socket
        int sock = socket(addr_family, SOCK_STREAM, ip_protocol);

        if (sock < 0) {
            ESP_LOGE(TAG, "Unable to create socket: errno %s\n", strerror(errno));
            break;
        }
        
        ESP_LOGI(TAG, "Socket created, connecting to %s:%d", host_ip, PORT);

        int err =
            connect(sock, (struct sockaddr *)&dest_addr, sizeof(dest_addr));
        if (err != 0) {
            ESP_LOGE(TAG, "Socket unable to connect: errno %s\n", strerror(errno));
            break;
        }
        ESP_LOGI(TAG, "Successfully connected");
        
        //Send and Recevie message to and from server
        while (1) {
            vTaskDelay(pdMS_TO_TICKS(1000)); // delay for 1 seconds
            int err = send_pakcet(sock, 4);
            // int err = send(sock, payload, strlen(payload), 0);
            if (err < 0) {
                ESP_LOGE(TAG, "Error occurred during sending: errno %s\n", strerror(errno));
                break;
            }
            int len = recv(sock, rx_buffer, sizeof(rx_buffer) - 1, 0);
            // Error occurred during receiving
            if (len < 0) {
                ESP_LOGE(TAG, "recv failed: errno %s\n", strerror(errno));
                break;
            }
            // Data received
            else {
                rx_buffer[len] = 0;  // Null-terminate whatever we received and
                                     // treat like a string
                ESP_LOGI(TAG, "Received %d bytes from %s:", len, host_ip);
                ESP_LOGI(TAG, "%s", rx_buffer);
            }
        }

        if (sock != -1) {
            ESP_LOGE(TAG, "Shutting down socket and restarting...");
            shutdown(sock, 0);
            close(sock);
        }
    }
}
