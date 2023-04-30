#include "utils.h"

/* *****************************************************************************
 *                                                                             *
 *  ***********************    TIME AND GLOBAL    ***************************    *
 *                                                                             *
 *  *************** <><><><><><><><><><><><><><><><><><><><> *************    *
 *                                                                             *
 *****************************************************************************/

void init_global_vars() {
    HEADER_LENGTH = sizeof(hd_01234_t);
    CUSTOM_GLOBAL_EPOCH_MICROSECONDS = current_unix_timestamp();
    
}

void initialize_sntp(void) {
    ESP_LOGI(TAG, "Initializing SNTP");
    sntp_setoperatingmode(SNTP_OPMODE_POLL);
    sntp_setservername(0, NTP_SERVER);
    sntp_init();
}

void wait_for_sntp_sync() {
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
    return now;
}

uint32_t get_timestamp_from_custom_epoch(void) {
    uint64_t timestamp_us = current_unix_timestamp();
    return (uint32_t)(timestamp_us - CUSTOM_GLOBAL_EPOCH_MICROSECONDS);
}

/* *****************************************************************************
 *                                                                             *
 *  ***********************    VARIABLE GENERATORS    ***************************    *
 *                                                                             *
 *  *************** <><><><><><><><><><><><><><><><><><><><> *************    *
 *                                                                             *
 *****************************************************************************/

//TODO: add random generating functions for each data type