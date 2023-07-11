cmake_minimum_required(VERSION 3.16)





set(WIFI_SSID $ENV{WIFI_SSID})
set(WIFI_PASSWORD $ENV{WIFI_PASSWORD})
set(CONTROLLER_SERVER_HOST $ENV{CONTROLLER_SERVER_HOST})
set(DEFAULT_PROTOCOL_ID $ENV{DEFAULT_PROTOCOL_ID})
set(DEFAULT_TRANSPORT_LAYER $ENV{DEFAULT_TRANSPORT_LAYER})
set(DISCONTINUOUS_TIMEOUT $ENV{DISCONTINUOUS_TIMEOUT})
set(CONTROLLER_TCP_PORT $ENV{CONTROLLER_TCP_PORT})
set(CONTROLLER_UDP_PORT $ENV{CONTROLLER_UDP_PORT})


configure_file(config.h.in ${CMAKE_BINARY_DIR}/config.h)

include_directories(${CMAKE_BINARY_DIR})

if("${IDF_TARGET}" STREQUAL "linux")

    list(APPEND EXTRA_COMPONENT_DIRS "$ENV{IDF_PATH}/tools/mocks/freertos/")
    list(APPEND EXTRA_COMPONENT_DIRS "./components")
    set(COMPONENTS main wifi ble protocol_examples_common)
    set(SRCS "main.c" )
endif()
include($ENV{IDF_PATH}/tools/cmake/project.cmake)
project(iot_project)