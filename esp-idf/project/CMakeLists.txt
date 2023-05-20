cmake_minimum_required(VERSION 3.16)

if("${IDF_TARGET}" STREQUAL "linux")
    list(APPEND EXTRA_COMPONENT_DIRS "$ENV{IDF_PATH}/tools/mocks/freertos/"
                    "$ENV{IDF_PATH}/examples/protocols/linux_stubs/esp_stubs")
    list(APPEND EXTRA_COMPONENT_DIRS "./components")
    set(COMPONENTS main wifi ble)
    set(SRCS "main.c" )

    include($ENV{IDF_PATH}/tools/cmake/project.cmake)
project(iot_project)