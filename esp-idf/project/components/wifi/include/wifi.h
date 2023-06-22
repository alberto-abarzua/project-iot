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
#include "esp_netif.h"
#include "freertos/task.h"
#include "lwip/apps/sntp.h"
#include "lwip/dns.h"
#include "lwip/netdb.h"
#include "protocol_examples_common.h"
#include "sdkconfig.h"
#include "utils.h"

#define HOST_IP_ADDR CONFIG_IPV4_ADDR
#define TCP_PORT CONFIG_PORT_TCP
#define UDP_PORT CONFIG_PORT_UDP
#define HANDSHAKE_PORT CONFIG_PORT_HANDSHAKE
#define TCP_TIMEOUT CONFIG_TCP_TIMEOUT
#define UDP_TIMEOUT CONFIG_UDP_TIMEOUT



// Functions


void tcp_client(int protocol_id);
void udp_client(int protocol_id);
int send_pakcet_tcp(int sock, int protocol_id);
int send_pakcet_udp(int sock, struct sockaddr_in *in_addr, int protocol_id);
int handshake(config_t *, char, uint16_t);


void main_wifi(void);
#endif  // wifi_h