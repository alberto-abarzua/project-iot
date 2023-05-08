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

void init_global_vars() {
    HEADER_LENGTH = sizeof(hd_01234_t);
    CUSTOM_GLOBAL_EPOCH_MICROSECONDS = current_unix_timestamp();
    // log custom
    ESP_LOGI(TAG, "HEADER_LENGTH: %d", HEADER_LENGTH);
    ESP_LOGI(TAG, "CUSTOM_GLOBAL_EPOCH_MICROSECONDS: %llu",
             CUSTOM_GLOBAL_EPOCH_MICROSECONDS);
}

void initialize_sntp(
    void) {  // not going to be used RN (no internet access in this case)
    ESP_LOGI(TAG, "Initializing SNTP");
    sntp_setoperatingmode(SNTP_OPMODE_POLL);
    sntp_setservername(0, NTP_SERVER);
    sntp_init();
}

void wait_for_sntp_sync() {  // Same as initialize_sntp
    time_t now = 0;
    struct tm timeinfo = {0};
    int retry = 0;
    const int retry_count = 10;

    while (timeinfo.tm_year < (2016 - 1900) && ++retry < retry_count) {
        ESP_LOGI(TAG, "Waiting for system time to be set... (%d/%d)", retry,
                 retry_count);
        vTaskDelay(2000 / portTICK_PERIOD_MS);
        time(&now);
        localtime_r(&now, &timeinfo);
    }
}

uint64_t current_unix_timestamp() {
    struct timeval tv;
    gettimeofday(&tv, NULL);
    uint64_t now = (uint64_t)tv.tv_sec * 1000 + (uint64_t)tv.tv_usec / 1000;
    return now;  // milliseconds
}

uint32_t get_timestamp_from_custom_epoch(void) {
    return (uint32_t)current_unix_timestamp();
    // CODE BELLOW TO USE WITH SNTP
    // uint64_t timestamp_us = current_unix_timestamp();
    // return (uint32_t)(timestamp_us - CUSTOM_GLOBAL_EPOCH_MICROSECONDS);
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