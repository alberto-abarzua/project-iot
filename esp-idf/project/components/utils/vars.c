#include "utils.h"

/* *****************************************************************************
 *                                                                             *
 *  ***********************    TIME AND GLOBAL    *************************** *
 *                                                                             *
 *  *************** <><><><><><><><><><><><><><><><><><><><> *************    *
 *                                                                             *
 *****************************************************************************/

uint16_t HEADER_LENGTH;
uint64_t CUSTOM_GLOBAL_EPOCH_MICROSECONDS;
uint8_t DEVICE_MAC_ADDRESS[6];
uint16_t DEVICE_ID;

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

void init_global_vars() {
    HEADER_LENGTH = sizeof(hd_01234_t);
    CUSTOM_GLOBAL_EPOCH_MICROSECONDS = current_unix_timestamp();
    ESP_ERROR_CHECK(nvs_flash_init());
    get_mac_address(DEVICE_MAC_ADDRESS);
    generate_device_id(DEVICE_MAC_ADDRESS, &DEVICE_ID);
    // log custom
    ESP_LOGI(TAG, "HEADER_LENGTH: %d", HEADER_LENGTH);
    ESP_LOGI(TAG, "CUSTOM_GLOBAL_EPOCH_MICROSECONDS: %llu",
             CUSTOM_GLOBAL_EPOCH_MICROSECONDS);
}

uint64_t current_unix_timestamp() {
    struct timeval tv;
    gettimeofday(&tv, NULL);
    uint64_t now = (uint64_t)tv.tv_sec * 1000 + (uint64_t)tv.tv_usec / 1000;
    return now;  // milliseconds
}

uint32_t get_timestamp_from_custom_epoch(void) {
    return (uint32_t)current_unix_timestamp();
}

esp_err_t set_nvs_config(config_t config) {
    nvs_handle_t my_handle;
    esp_err_t ret = nvs_open("storage", NVS_READWRITE, &my_handle);
    if (ret != ESP_OK) {
        printf("Error (%s) opening NVS handle!\n", esp_err_to_name(ret));
        return ret;
    }

    ret = nvs_set_blob(my_handle, "config_key", &config, sizeof(config));
    if (ret != ESP_OK) {
        printf("Error (%s) writing!\n", esp_err_to_name(ret));
        nvs_close(my_handle);
        return ret;
    }

    ret = nvs_commit(my_handle);
    if (ret != ESP_OK) {
        printf("Error (%s) committing!\n", esp_err_to_name(ret));
    }

    nvs_close(my_handle);
    return ret;
}

esp_err_t get_nvs_config(config_t *config) {
    nvs_handle_t my_handle;
    esp_err_t ret = nvs_open("storage", NVS_READONLY, &my_handle);
    if (ret == ESP_ERR_NVS_NOT_FOUND) {
        printf("The value is not initialized yet!\n");
        config->protocol_id = DEFAULT_PROTOCOL_ID;
        config->trans_layer = DEFAULT_TRANS_LAYER;
    }else if (ret != ESP_OK) {
        printf("Error (%s) opening NVS handle!\n", esp_err_to_name(ret));
        return ret;
    }

    size_t required_size = sizeof(config_t);
    ret = nvs_get_blob(my_handle, "config_key", config, &required_size);
    if (ret == ESP_ERR_NVS_NOT_FOUND) {
        printf("The value is not initialized yet!\n");
        config->protocol_id = DEFAULT_PROTOCOL_ID;
        config->trans_layer = DEFAULT_TRANS_LAYER;
    }else if (ret != ESP_OK) {
        printf("Error (%s) reading!\n", esp_err_to_name(ret));
    }

    nvs_close(my_handle);
    return ret;
}

/* *****************************************************************************
 *                                                                             *
 *  ***********************    VARIABLE GENERATORS *************************** *
 *                                                                             *
 *  *************** <><><><><><><><><><><><><><><><><><><><> *************    *
 *                                                                             *
 *****************************************************************************/

// TODO: add random generating functions for each data type

char val1() { return (char)1; }

char batt_level() {
    return (char)((uint64_t)(get_timestamp_from_custom_epoch() / 10e6) % 100);
}

char temp() {
    return (char)(((uint64_t)(get_timestamp_from_custom_epoch() / 6e2) % 26) +
                  5);
}

uint32_t press() {
    return (((uint64_t)(get_timestamp_from_custom_epoch() / 6e2) % 201) + 1000);
}

char hum() {
    return (char)(((uint64_t)(get_timestamp_from_custom_epoch() / 6e2) % 51) +
                  30);
}

uint32_t co() {
    return (((uint64_t)(get_timestamp_from_custom_epoch() / 6e2) % 171) + 30);
}

float random_float(float min, float max) {
    float scale = rand() / (float)RAND_MAX; /* [0, 1.0] */
    return min + scale * (max - min);       /* [min, max] */
}

uint32_t ampx() { return random_float(0.0059, 0.12); }

uint32_t freqx() { return random_float(29.0, 31.0); }

uint32_t ampy() { return random_float(0.0041, 0.11); }

uint32_t freqy() { return random_float(59.0, 61.0); }

uint32_t ampz() { return random_float(0.008, 0.15); }

uint32_t freqz() { return random_float(89.0, 91.0); }

uint32_t rms() {
    return sqrt(pow(ampx(), 2) + pow(ampy(), 2) + pow(ampz(), 2));
}

void accx(char *buf) {
    float *write_ptr = (float *)buf;
    for (int i = 0; i < 2000; i++) {
        write_ptr[i] = 2.0f * sinf(2.0f * M_PI * 0.001f * (float)i);
    }
}

void accy(char *buf) {
    float *write_ptr = (float *)buf;
    for (int i = 0; i < 2000; i++) {
        write_ptr[i] = 3.0f * sinf(2.0f * M_PI * 0.001f * (float)i);
    }
}

void accz(char *buf) {
    float *write_ptr = (float *)buf;
    for (int i = 0; i < 2000; i++) {
        write_ptr[i] = 10.0f * sinf(2.0f * M_PI * 0.001f * (float)i);
    }
}