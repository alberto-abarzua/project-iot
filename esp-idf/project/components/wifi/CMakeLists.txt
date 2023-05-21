

idf_component_register(SRCS "clients.c" 
                       INCLUDE_DIRS "include"
                       REQUIRES esp_netif protocol_examples_common utils)