/*
 * SPDX-FileCopyrightText: 2022 Espressif Systems (Shanghai) CO LTD
 *
 * SPDX-License-Identifier: Unlicense OR CC0-1.0
 */
#include <stdlib.h>

#include "esp_event.h"
#include "esp_netif.h"
#include "nvs_flash.h"
#include "protocol_examples_common.h"
#include "utils.h"

uint8_t mac[6];
uint16_t device_id;

void get_mac_address(uint8_t *mac) {
    int err = esp_efuse_mac_get_default(mac);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Error getting MAC address: %d", err);
        return;
    }

    ESP_LOGI(TAG, "MAC address: %02X:%02X:%02X:%02X:%02X:%02X", mac[0], mac[1],
             mac[2], mac[3], mac[4], mac[5]);
}
void generate_device_id(const uint8_t *mac, uint16_t *device_id) {
    *device_id = (mac[0] ^ mac[3]) | ((mac[1] ^ mac[4]) << 8) |
                 ((mac[2] ^ mac[5]) << 16);
}

void app_main(void) {
    ESP_ERROR_CHECK(nvs_flash_init());
    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());

    /* This helper function configures Wi-Fi or Ethernet, as selected in
     * menuconfig. Read "Establishing Wi-Fi or Ethernet Connection" section in
     * examples/protocols/README.md for more information about this function.
     */
    
    ESP_ERROR_CHECK(example_connect());
    init_global_vars();
    char restart = '0';
    // Initialize and synchronize the SNTP client
    initialize_sntp();
    wait_for_sntp_sync();
    get_mac_address(mac);
    generate_device_id(mac, &device_id);
    while (1) {
        config_t config;
        handshake(&config, restart, device_id);
        restart = '1';
        if (config.trans_layer == 'U') {
            udp_client(config.protocol_id);
        } else {
            tcp_client(config.protocol_id);
        }
    }
}
