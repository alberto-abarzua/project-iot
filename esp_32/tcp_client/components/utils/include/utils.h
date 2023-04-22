#ifndef utils_h
#define utils_h
#include <arpa/inet.h>
#include <errno.h>
#include <netdb.h>  // struct addrinfo
#include <stdint.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>
#include "esp_log.h"
#include "esp_netif.h"
#include "sdkconfig.h"
#include "freertos/task.h"

#define HOST_IP_ADDR CONFIG_EXAMPLE_IPV4_ADDR

#define PORT CONFIG_EXAMPLE_PORT
#define TAG "ESP_32"
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

void tcp_client(void);
int send_packet_protocol0(int sock);
int send_pakcet(int sock, int protocol_id);

#endif  // utils_h