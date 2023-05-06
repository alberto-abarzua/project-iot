#!/bin/sh

# Load the .env file
export $(grep -v '^#' .env | xargs)

init_esp_flash_server() {
    cd ./esp-idf/esp_flash_server
    ls -la
    pdm install
    pdm run python esp_rfc2217_server.py -p ${ESP_RFC2217_PORT} ${ESP_DEVICE_PORT}
}

# Function to flash the ESP-32
build_flash_esp32() {
    sleep 2
    echo "Flashing ESP-32..."
    docker compose run esp-idf build flash

    if [ $? -eq 0 ]; then
        echo "ESP-32 flashed successfully."
        return 0
    else
        echo "Failed to flash ESP-32."
        return 1
    fi
}

# Function to clean up on exit
cleanup() {
    echo "Cleaning up..."
    docker compose down --remove-orphans --timeout 5
    pkill -f esp_rfc2217_server.py
}

startup() {
    docker compose down --remove-orphans
}

trap cleanup INT

# Core logic
init_esp_flash_server &

startup &

case "$1" in
menuconfig)
    echo "Running config"
    docker compose run esp-idf menuconfig
    ;;
monitor)
    echo "Running monitor"
    docker compose up --build server db adminer esp-idf
    ;;
build)
    echo "Running build"
    docker compose build esp-idf
    docker compose run esp-idf build
    ;;
flashonly)
    build_flash_esp32
    if [ $? -eq 1 ]; then
        echo "Exiting due to flash failure."
    fi
    ;;
flash)
    build_flash_esp32
    if [ $? -eq 1 ]; then
        echo "Exiting due to flash failure."
    fi
    docker compose up server db adminer esp-idf
    ;;
*)
    echo "Running default"
    docker compose up --build server db adminer esp-idf
    ;;
esac

cleanup &
