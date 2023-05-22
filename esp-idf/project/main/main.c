#include <stdlib.h>

#include "nvs_flash.h"

#include "wifi.h"
#include "ble.h"
#include "utils.h"

void app_main(void) {
    ESP_ERROR_CHECK(nvs_flash_init());
    init_global_vars();
    main_wifi();
    // main_ble();
}