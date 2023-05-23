#!/bin/bash

# Load the .env file
export $(grep -v '^#' .env | xargs)

# Function to clean up on exit
cleanup() {
    echo "Cleaning up..."
    kill $DC_PID

    docker compose down --remove-orphans --timeout 5
}

startup() {
    docker compose down --remove-orphans
}






case "$1" in
idf)
    echo "Running config"
    cd ./esp-idf/project/
    . $HOME/esp/esp-idf/export.sh
    # if second arg is menuconfig
    if [ "$2" = "menuconfig" ]; then
        if [ ! -f ./sdkconfig ]; then
            echo "sdkconfig not found, generating..."
            python3 ./generate_kconfig.py
        fi
        idf.py menuconfig

    else
        idf.py ${@:2}
    fi
    ;;
dev)
    # startup &
    echo "Running all services in dev mode"
    # trap cleanup INT
    # docker compose up --build &
    # cd ./esp-idf/project/ 
    # . $HOME/esp/esp-idf/export.sh
    # idf.py build flash monitor &
    # DC_PID=$!
    # cd ./../../
    cd ./rasp/
    pdm install
    pdm run src/main.py
    # cleanup &

    ;;

esac

