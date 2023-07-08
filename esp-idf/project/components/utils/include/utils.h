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
#define MAX_IP_ADDR_LEN 15
#define MAX_SSID_LEN 32
#define MAX_PASSWORD_LEN 64



#include <sys/time.h>
#pragma pack(push, 1)
typedef struct hd_12345 {
    uint16_t id_device;
    uint8_t MAC[6];
    char trans_layer;
    char protocol_id;
    uint16_t msg_len;
} hd_12345_t;
#pragma pack(pop)

#pragma pack(push, 1)
typedef struct ds_p1234 {
    char data1;
    int32_t data2;
    char data3;
    int32_t data4;
    char data5;
    int32_t data6;
    int32_t data7;
    int32_t data8;
    int32_t data9;
    int32_t data10;
    int32_t data11;
    int32_t data12;
    int32_t data13;
} ds_p1234_t;
#pragma pack(pop)

#pragma pack(push, 1)
typedef struct ds_p5 {
    char data1;
    int32_t data2;
    char data3;
    int32_t data4;
    char data5;
    int32_t data6;
    char *data7;
    char *data8;
    char *data9;
    char *data10;
    char *data11;
    char *data12;
    
} ds_p5_t;
#pragma pack(pop)
typedef struct config {
    int status;
    char protocol_id; // 1,2,3,4,5
    int bmi270_sampling;
    int bmi270_sensibility;
    int bmi270_gyro_sensibility;
    int bme688_sampling;
    int discontinuous_time;
    int tcp_port;
    int udp_port;
    char host_ip_addr[64];
    char ssid[32];
    char password[64];
    char trans_layer;  // U for UDP, T for TCP

} config_t;

// Functions
extern uint16_t HEADER_LENGTH;
extern uint64_t CUSTOM_GLOBAL_EPOCH_MICROSECONDS;
extern uint8_t DEVICE_MAC_ADDRESS[6];
extern uint16_t DEVICE_ID;

void parse_config(char * , config_t *config);
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
void random_between_array(float min, float max, char *buf);
void print_config(config_t config);
#endif  // utils_h
