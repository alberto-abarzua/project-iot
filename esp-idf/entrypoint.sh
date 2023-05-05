#!/usr/bin/env bash

# This runs inside the container

set -e

. $IDF_PATH/export.sh

export ESPTOOLPY_NO_STUB=1
FLASH_PORT="rfc2217://host.docker.internal:${ESP_RFC2217_PORT}?ign_set_control"

sleep 2
python3 /usr/local/bin/generate_kconfig.py 
cd /workspace
if [ "$1" = "lint" ]; then
    echo "Running cppcheck..."
    cppcheck --enable=all --std=c11 -i build/ .

elif [ $# -eq 0 ]; then

    idf.py -p ${FLASH_PORT} monitor

else 

    idf.py -p ${FLASH_PORT} "$@"

fi

