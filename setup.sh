#!/bin/bash

install_docker_engine_debian(){
    echo "Starting installation script for DOCKER ENGINE on a DEBIAN base system..."
    echo "Script base on commands from: https://docs.docker.com/engine/install/debian/"

    echo "Updating package lists..."
    sudo apt-get update

    echo "Installing dependencies..."
    sudo sudo apt-get install ca-certificates curl gnupg

    echo "Adding docker official GPG key..."
    sudo install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    sudo chmod a+r /etc/apt/keyrings/docker.gpg

    echo "Setting up repository"
    echo \
    "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
    "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
    sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

    echo "Update package lists AGAIN..."
    sudo apt-get update

    echo "Installing latests Docker Engine, Container and Docker Compose..."    
    sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

    echo "Add current user to docker group..."
    sudo usermod -aG docker $USER

    echo "Docker Engine has been installed successfully."

}

install_docker_engine_ubuntu(){
    echo "Starting installation script for DOCKER ENGINE on a UBUNTU base system..."
    echo "Script base on commands from: https://docs.docker.com/engine/install/ubuntu/"

    echo "Updating package lists..."
    sudo apt-get update

    echo "Installing dependencies..."
    sudo sudo apt-get install ca-certificates curl gnupg

    echo "Adding Dockers official GPG key..."    
    sudo install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    sudo chmod a+r /etc/apt/keyrings/docker.gpg

    echo "Setting up docker repository"
    echo \
    "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
    "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
    sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

    echo "Updating package lists..."
    sudo apt-get update

    echo "Installing latests Docker Engine, Container and Docker Compose..."    
    sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

    echo "Add current user to docker group..."
    sudo usermod -aG docker $USER

    echo "Docker Engine has been installed successfully."
}

#!/bin/bash
# Check if the distribution is Ubuntu-based
if grep -q "ubuntu" /etc/os-release; then
    echo "This is an Ubuntu-based distribution."
    install_docker_engine_ubuntu
# Check if the distribution is Debian-based
elif grep -q "debian" /etc/os-release; then
    echo "This is a Debian-based distribution."
    install_docker_engine_debian
# If the distribution is neither Debian nor Ubuntu-based
else
    echo "This distribution is not supported."
    exit 1
fi
