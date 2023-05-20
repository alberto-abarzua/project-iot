#include <stdlib.h>

#include "nvs_flash.h"

#include "wifi.h"
#include "ble.h"


void app_main(void) {
    ESP_ERROR_CHECK(nvs_flash_init());
    // main_wifi();
}
