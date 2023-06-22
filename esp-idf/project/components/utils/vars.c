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

void parse_config(char *buffer, config_t *config) {
    int current = 3;  // Skip "con"

    memcpy(&config->status, &buffer[current], sizeof(int32_t));
    current += sizeof(int32_t);
    // memcpy(&config->protocol_id, &buffer[current], sizeof(int32_t));
    config->protocol_id = (uint8_t)buffer[current];
    current += sizeof(int32_t);
    memcpy(&config->bmi270_sampling, &buffer[current], sizeof(int32_t));
    current += sizeof(int32_t);
    memcpy(&config->bmi270_sensibility, &buffer[current], sizeof(int32_t));
    current += sizeof(int32_t);
    memcpy(&config->bmi270_gyro_sensibility, &buffer[current], sizeof(int32_t));
    current += sizeof(int32_t);
    memcpy(&config->bme688_sampling, &buffer[current], sizeof(int32_t));
    current += sizeof(int32_t);
    memcpy(&config->discontinuous_time, &buffer[current], sizeof(int32_t));
    current += sizeof(int32_t);
    memcpy(&config->tcp_port, &buffer[current], sizeof(int32_t));
    current += sizeof(int32_t);
    memcpy(&config->udp_port, &buffer[current], sizeof(int32_t));
    current += sizeof(int32_t);

    int32_t host_ip_addr_len;
    memcpy(&host_ip_addr_len, &buffer[current], sizeof(int32_t));
    current += sizeof(int32_t);
    host_ip_addr_len =
        host_ip_addr_len > MAX_IP_ADDR_LEN ? MAX_IP_ADDR_LEN : host_ip_addr_len;
    memcpy(config->host_ip_addr, &buffer[current], host_ip_addr_len);
    config->host_ip_addr[host_ip_addr_len] = '\0';  // Null terminate
    current += host_ip_addr_len;

    int32_t ssid_len;
    memcpy(&ssid_len, &buffer[current], sizeof(int32_t));
    current += sizeof(int32_t);
    ssid_len = ssid_len > MAX_SSID_LEN ? MAX_SSID_LEN : ssid_len;
    memcpy(config->ssid, &buffer[current], ssid_len);
    config->ssid[ssid_len] = '\0';  // Null terminate
    current += ssid_len;

    int32_t password_len;
    memcpy(&password_len, &buffer[current], sizeof(int32_t));
    current += sizeof(int32_t);
    password_len =
        password_len > MAX_PASSWORD_LEN ? MAX_PASSWORD_LEN : password_len;
    memcpy(config->password, &buffer[current], password_len);
    config->password[password_len] = '\0';  // Null terminate
    current += password_len;

    memcpy(&config->trans_layer, &buffer[current], sizeof(char));
    current += sizeof(char);
}

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
    HEADER_LENGTH = sizeof(hd_12345_t);
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

void print_config(config_t config) {
    printf("Status: %d\n", config.status);
    printf("Protocol ID: %d\n", (int)config.protocol_id);
    printf("BMI270 Sampling: %d\n", config.bmi270_sampling);
    printf("BMI270 Sensibility: %d\n", config.bmi270_sensibility);
    printf("BMI270 Gyro Sensibility: %d\n", config.bmi270_gyro_sensibility);
    printf("BME688 Sampling: %d\n", config.bme688_sampling);
    printf("Discontinuous Time: %d\n", config.discontinuous_time);
    printf("TCP Port: %d\n", config.tcp_port);
    printf("UDP Port: %d\n", config.udp_port);
    printf("Host IP Address: %s\n", config.host_ip_addr);
    printf("SSID: %s\n", config.ssid);
    printf("Password: %s\n", config.password);
    printf("Transport Layer: %c\n", config.trans_layer);
}

int check_diff_config(config_t *c1, config_t* c2) {
    // TODO: check if there is a difference between the two configs, print the
    // values that differ
    return 1; 
}

esp_err_t set_nvs_config(config_t config) {
    config_t current_config;
    get_nvs_config(&current_config);

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
    // show both configs
    printf("Current Config:\n");
    print_config(current_config);
    printf("New Config:\n");
    print_config(config);
    check_diff_config(&current_config,&config);
    if (current_config.protocol_id != config.protocol_id ||
        current_config.status != config.status ||
        current_config.trans_layer != config.trans_layer

    ) {
        ESP_LOGI(TAG, "Restarting ESP");
        esp_restart();
    }
    return ret;
}

esp_err_t get_nvs_config(config_t *config) {
    nvs_handle_t my_handle;
    esp_err_t ret = nvs_open("storage", NVS_READONLY, &my_handle);
    if (ret == ESP_ERR_NVS_NOT_FOUND) {
        printf("The value is not initialized yet!\n");

        config->protocol_id = DEFAULT_PROTOCOL_ID;
        config->trans_layer = DEFAULT_TRANS_LAYER;

        config->udp_port = CONFIG_PORT_UDP;
        config->tcp_port = CONFIG_PORT_TCP;

        memcpy(config->host_ip_addr, CONFIG_IPV4_ADDR,
               strlen(CONFIG_IPV4_ADDR));
        //add null terminator
        config->host_ip_addr[strlen(CONFIG_IPV4_ADDR)] = '\0';

        memcpy(config->ssid, CONFIG_EXAMPLE_WIFI_SSID,
               strlen(CONFIG_EXAMPLE_WIFI_SSID));
        //add null terminator
        config->ssid[strlen(CONFIG_EXAMPLE_WIFI_SSID)] = '\0';
        memcpy(config->password, CONFIG_EXAMPLE_WIFI_PASSWORD,
               strlen(CONFIG_EXAMPLE_WIFI_PASSWORD));
        //add null terminator
        config->password[strlen(CONFIG_EXAMPLE_WIFI_PASSWORD)] = '\0';

        config->discontinuous_time =1;
        config->bmi270_sampling = 1;
        config->bmi270_sensibility = 1;
        config->bmi270_gyro_sensibility = 1;
        config->bme688_sampling = 1;
        config->status = 1;
            

    } else if (ret != ESP_OK) {
        printf("Error (%s) opening NVS handle!\n", esp_err_to_name(ret));
        return ret;
    }

    size_t required_size = sizeof(config_t);
    ret = nvs_get_blob(my_handle, "config_key", config, &required_size);
    if (ret == ESP_ERR_NVS_NOT_FOUND) {
        printf("The value is not initialized yet!\n");
        config->protocol_id = DEFAULT_PROTOCOL_ID;
        config->trans_layer = DEFAULT_TRANS_LAYER;
    } else if (ret != ESP_OK) {
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

void random_between_array(float min, float max, char *buf) {
    float *write_ptr = (float *)buf;
    for (int i = 0; i < 2000; i++) {
        write_ptr[i] = random_float(min, max);
    }
}