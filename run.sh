#!/bin/sh

# Load the .env file
export $(grep -v '^#' .env | xargs)

# Function to flash the ESP-32
flash_esp32() {
    echo "Flashing ESP-32..."
    docker compose build esp-idf
    docker compose run esp-idf /bin/bash -c "cd /workspace && idf.py build && idf.py -p ${ESP_DEVICE} flash"
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
}

# Handle ctrl+c (SIGINT)
trap cleanup INT

# clean up any existing containers
docker compose down --remove-orphans
# Run desired services based on the .env variable
echo "$1"
if [ "$TARGET_SERVICES" = "dev" ]; then
    if [ "$1" = "menuconfig" ]; then
        echo "runing config"
        docker compose run esp-idf /bin/bash -c "cd /workspace && idf.py menuconfig"
    elif [ "$1" = "monitor" ]; then
        echo "runing monitor"
        docker compose up --build server db adminer esp-idf
    else
        flash_esp32
        if [ $? -eq 1 ]; then
            echo "Exiting due to flash failure."
            exit 1
        fi
        docker compose up --build server db adminer esp-idf
    fi
elif [ "$TARGET_SERVICES" = "deploy_no_adminer" ]; then
    docker compose up --build server db
elif [ "$TARGET_SERVICES" = "deploy" ]; then
    docker compose up --build server db adminer
else
    echo "Invalid TARGET_SERVICES value in .env file. Please update and try again."
fi
