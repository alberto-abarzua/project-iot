

idf_component_register(SRCS "packets.c" "clients.c" "vars.c"
                       INCLUDE_DIRS "include"
                       REQUIRES esp_netif protocol_examples_common)