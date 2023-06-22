#include <stdlib.h>

#include "ble.h"
#include "utils.h"
#include "wifi.h"

void app_main(void) {
    init_global_vars();
    config_t config;
    get_nvs_config(&config);
    print_config(config);
    ESP_LOGI(TAG, "config.trans_layer %c config.protocol_id %d",
             config.trans_layer, config.protocol_id);
    if (config.trans_layer == 'U' || config.trans_layer == 'T') {
        main_wifi();
    } else if (config.trans_layer == 'C' || config.trans_layer == 'D') {
        main_ble(config.trans_layer);
    }
}