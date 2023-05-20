cmake_minimum_required(VERSION 3.16)

if("${IDF_TARGET}" STREQUAL "linux")

    list(APPEND EXTRA_COMPONENT_DIRS "$ENV{IDF_PATH}/tools/mocks/freertos/")
    list(APPEND EXTRA_COMPONENT_DIRS "./components")
    set(COMPONENTS main wifi ble protocol_examples_common)
    set(SRCS "main.c" )
endif()
include($ENV{IDF_PATH}/tools/cmake/project.cmake)
project(iot_project)