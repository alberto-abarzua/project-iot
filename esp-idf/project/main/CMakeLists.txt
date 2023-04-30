if(${IDF_TARGET} STREQUAL "linux")
    set(requires esp_stubs protocol_examples_common nvs_flash)
endif()


idf_component_register(SRCS "main.c" 
                                INCLUDE_DIRS "."
                                REQUIRES ${requires})
