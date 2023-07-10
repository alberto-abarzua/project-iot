#!/bin/bash

# Load the .env file
export $(grep -v '^#' .env | xargs)

get_ip() {
    echo $(hostname -I | awk '{print $1}')
}

init_idf() {
    echo "Running config"
    cd ./esp-idf/project/
    echo "Requires idf.py to be installed and environment variables to be set"
    if [ -z "$IDF_PATH" ]; then
        echo "IDF_PATH is not set"
        exit 1
    fi
}

export CONTROLLER_SERVER_HOST=$(get_ip)

case "$1" in
idf)
    init_idf
    shift
    idf.py "$@"
    ;;
dev)
    # startup &
    echo "Running all services in dev mode"
    cd ./rasp/
    pdm install
    pdm run src/main.py
    ;;

devgui)
    # startup &
    echo "Running all services in dev mode"
    cd ./rasp/
    pdm install
    pdm run src/gui.py
    ;;
run)
    docker-compose up -d
    cd ./rasp/
    pdm install
    pdm run src/main.py
    docker-compose down --remove-orphans
    ;;

rungui_rasp)
    docker-compose up -d
    cd ./rasp/
    # create venv
    python3 -m venv venv
    # activate venv
    ./venv/bin/activate
    pip install -r requirements.txt
    python3 src/gui.py
    
    docker-compose down --remove-orphans
    ;;
*)
    echo "Usage: $0 {idf|dev|run}"
    exit 1
    ;;
esac
