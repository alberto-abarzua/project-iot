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
#include "freertos/task.h"
#include "sdkconfig.h"

#define HOST_IP_ADDR CONFIG_EXAMPLE_IPV4_ADDR
#define TCP_PORT CONFIG_TCP_PORT
#define UDP_PORT CONFIG_UDP_PORT
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
int send_pakcet_tcp(int sock, int protocol_id);
int send_pakcet_udp(int sock, struct sockaddr_in *in_addr, int protocol_id);
void udp_client(void);
#endif  // utils_h