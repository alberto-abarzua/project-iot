#!/bin/bash
# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

install_docker_engine_debian(){
    echo -e "${GREEN}Starting installation script for DOCKER ENGINE on a DEBIAN base system...${NC}"
    echo -e "${GREEN}Script base on commands from: https://docs.docker.com/engine/install/debian/${NC}"

    echo -e "${GREEN}Updating package lists...${NC}"
    sudo apt-get update

    echo -e "${GREEN}Installing dependencies...${NC}"
    sudo sudo apt-get install ca-certificates curl gnupg

    echo -e "${GREEN}Adding docker official GPG key...${NC}"
    sudo install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    sudo chmod a+r /etc/apt/keyrings/docker.gpg

    echo -e "${GREEN}Setting up repository${NC}"
    echo \
    "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
    "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
    sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

    echo -e "${GREEN}Update package lists AGAIN...${NC}"
    sudo apt-get update

    echo -e "${GREEN}Installing latests Docker Engine, Container and Docker Compose...${NC}" 
    sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

    echo -e "${GREEN}Add current user to docker group...${NC}"
    sudo usermod -aG docker $USER

    echo -e "${GREEN}Docker Engine has been installed successfully.${NC}"

}

install_docker_engine_ubuntu(){
    echo -e "${GREEN}Starting installation script for DOCKER ENGINE on a UBUNTU base system...${NC}"
    echo -e "${GREEN}Script base on commands from: https://docs.docker.com/engine/install/ubuntu/${NC}"

    echo -e "${GREEN}Updating package lists...${NC}"
    sudo apt-get update

    echo -e "${GREEN}Installing dependencies...${NC}"
    sudo sudo apt-get install ca-certificates curl gnupg

    echo -e "${GREEN}Adding Dockers official GPG key...${NC}"
    sudo install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    sudo chmod a+r /etc/apt/keyrings/docker.gpg

    echo -e "${GREEN}Setting up docker repository${NC}"
    echo \
    "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
    "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
    sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

    echo -e "${GREEN}Updating package lists...${NC}"
    sudo apt-get update

    echo -e "${GREEN}Installing latests Docker Engine, Container and Docker Compose...${NC}"    
    sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

    echo -e "${GREEN}Add current user to docker group...${NC}"
    sudo usermod -aG docker $USER

    echo -e "${GREEN}Docker Engine has been installed successfully.${NC}"
}

#!/bin/bash
# Check if the distribution is Ubuntu-based
if grep -q "ubuntu" /etc/os-release; then
    echo -e "${GREEN}This is an Ubuntu-based distribution.${NC}"
    install_docker_engine_ubuntu
# Check if the distribution is Debian-based
elif grep -q "debian" /etc/os-release; then
    echo -e "${GREEN}This is a Debian-based distribution.${NC}"
    install_docker_engine_debian
# If the distribution is neither Debian nor Ubuntu-based
else
    echo -e "${GREEN}This distribution is not supported.${NC}"
    exit 1
fi

echo -e "${GREEN}Installing Git...${GREEN}"
sudo apt-get install git

ip_address=$(ifconfig wlo1 | grep 'inet ' | grep -v '127.0.0.1' | awk '{print $2}')

# Echo the IP address to the console in green color
echo -e "${YELLOW}Your IP address is: $ip_address${NC}"
echo "Use this to set up the .env file from the .env.template..."

