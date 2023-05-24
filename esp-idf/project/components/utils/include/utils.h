#ifndef utils_h
#define utils_h
#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif
#include <unistd.h>
#include "sdkconfig.h"
#include <math.h>
#include <stdint.h>
#include "esp_log.h"
#include <string.h>
#include "esp_mac.h"
#include "nvs_flash.h"
#include "nvs.h"
#include "esp_system.h"

#define TAG "ESP_32"


#define DEFAULT_TRANS_LAYER 'C'
#define DEFAULT_PROTOCOL_ID 0

#include <sys/time.h>
#pragma pack(push, 1)
typedef struct hd_01234 {
    uint16_t id_device;
    uint8_t MAC[6];
    char trans_layer;
    char protocol_id;
    uint16_t msg_len;
} hd_01234_t;
#pragma pack(pop)

#pragma pack(push, 1)
typedef struct ds_p0123 {
    char data1;
    char data2;
    int32_t data3;
    char data4;
    int32_t data5;
    char data6;
    int32_t data7;
    int32_t data8;
    int32_t data9;
    int32_t data10;
    int32_t data11;
    int32_t data12;
    int32_t data13;
    int32_t data14;
} ds_p0123_t;
#pragma pack(pop)

#pragma pack(push, 1)
typedef struct ds_p4 {
    char data1;
    char data2;
    int32_t data3;
    char data4;
    int32_t data5;
    char data6;
    int32_t data7;
    char *data8;
    char *data9;
    char *data10;
} ds_p4_t;
#pragma pack(pop)

typedef struct config {
    char trans_layer;  // U for UDP, T for TCP
    char protocol_id;  // 0,1,2,3,4
} config_t;

// Functions
extern uint16_t HEADER_LENGTH;
extern uint64_t CUSTOM_GLOBAL_EPOCH_MICROSECONDS;
extern uint8_t DEVICE_MAC_ADDRESS[6];
extern uint16_t DEVICE_ID;

uint32_t get_timestamp_from_custom_epoch(void);
uint64_t current_unix_timestamp();
char val1();
char batt_level();
char temp();
uint32_t press();
char hum();
uint32_t co();
float random_float(float min, float max);
uint32_t ampx();
uint32_t freqx();
uint32_t ampy();
uint32_t freqy();
uint32_t ampz();
uint32_t freqz();
uint32_t rms();
void accx(char *buf);
void accy(char *buf);
void accz(char *buf);
char *create_packet(int protocol_id, int *packet_size,char transport_layer);
void init_global_vars();
esp_err_t get_nvs_config(config_t *config);
esp_err_t set_nvs_config(config_t config);
#endif  // utils_h
