#ifndef wifi_h
#define wifi_h
// #include <arpa/inet.h>
#include <arpa/inet.h>
#include <errno.h>
#include <esp_sleep.h>
#include <math.h>
#include <netdb.h>
#include <stdint.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>

#include "esp_event.h"
#include "esp_log.h"
#include "esp_mac.h"
#include "esp_netif.h"
#include "freertos/task.h"
#include "lwip/apps/sntp.h"
#include "lwip/dns.h"
#include "lwip/netdb.h"
#include "protocol_examples_common.h"
#include "sdkconfig.h"
#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

#define NTP_SERVER "pool.ntp.org"
#define HOST_IP_ADDR CONFIG_IPV4_ADDR
#define TCP_PORT CONFIG_PORT_TCP
#define UDP_PORT CONFIG_PORT_UDP
#define HANDSHAKE_PORT CONFIG_PORT_HANDSHAKE
#define TCP_TIMEOUT CONFIG_TCP_TIMEOUT
#define UDP_TIMEOUT CONFIG_UDP_TIMEOUT
#define TAG "ESP_32"

extern uint16_t HEADER_LENGTH;
extern uint64_t CUSTOM_GLOBAL_EPOCH_MICROSECONDS;
extern uint8_t mac[6];
extern uint16_t device_id;
#pragma pack(push, 1)
typedef struct hd_01234 {
    int16_t id_device;
    char MAC[6];
    char trans_layer;
    char protocol_id;
    int16_t msg_len;
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

void tcp_client(int protocol_id);
void udp_client(int protocol_id);
int send_pakcet_tcp(int sock, int protocol_id);
int send_pakcet_udp(int sock, struct sockaddr_in *in_addr, int protocol_id);
int handshake(config_t *, char, uint16_t);
void initialize_sntp();
void wait_for_sntp_sync();
void init_global_vars();
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
void main_wifi(void);
char *create_packet(int protocol_id, int *packet_size);
#endif  // wifi_h