#ifndef utils_h
#define utils_h
#include <arpa/inet.h>
#include <errno.h>
#include <netdb.h>
#include <stdint.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>

#include "esp_log.h"
#include "esp_netif.h"
#include "freertos/task.h"
#include "lwip/apps/sntp.h"
#include "lwip/dns.h"
#include "lwip/netdb.h"
#include "sdkconfig.h"

#define NTP_SERVER "pool.ntp.org"
#define HOST_IP_ADDR CONFIG_EXAMPLE_IPV4_ADDR
#define TCP_PORT CONFIG_TCP_PORT
#define UDP_PORT CONFIG_UDP_PORT
#define HANDSHAKE_PORT CONFIG_HANDSHAKE_PORT
#define TCP_TIMEOUT 1000
#define UDP_TIMEOUT 1000
#define TAG "ESP_32"

uint16_t HEADER_LENGTH;
uint64_t CUSTOM_GLOBAL_EPOCH_MICROSECONDS;

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
#endif  // utils_h