# IoT Project - Communication between Raspberry Pi and ESP-32

---

## Prerequisites

- Install Docker Engine (or Desktop) to run the Docker Compose configuration for this project.
- Python 3
- Python PDM version 2.5.5

## Setup and Execution

1. Rename the `.env.template` file to `.env`.

2. Most of the variables in the `.env` file can be left unchanged for the project to work. However, you need to set the following required variables:
   - `ESP_FLASH_INTERNAL_IP`: The IP address of the host machine where the ESP is connected (used for flashing and monitoring)
   - `SESP_IPV4_ADDR`: The IP address that the ESP will target (IP of the Server).
   - `ESP_DEVICE_PORT`: The USB port to which the ESP is connected for flashing and monitoring. (The command "**ls /dev/tty**" can be used to identify in which USB port the ESP is plugged into. Might also need to run the command "**sudo chown <user> /dev/tty<USB_port_ESP>**" to give permission to the current user to use that port to flash and monitor de ESP)
   - `ESP_FLASH_INTERNAL_IP`: This is the IP of the device that will flash the ESP.

3. After making these changes make sure to run the command "**./run.sh menuconfig**" to set these variables up in the sdkconfig file of the ESP.

4. With all that said the most used command for development and debugging is "**./run.sh flash**". This command will run the containers server, db, Adminer and esp-idf. This in turn will run the server, create the database, give access to view the database through Adminer and finally build, flash and monitor the ESP connected to the machine.

## Running Server in a Raspberry Pi and ESP-32 transmitting data through the Raspberry's Wireless Access Point

1. Set-up a Raspberry Pi using this tutorial (Remember to upgrade software packages to their latest version)

   https://projects.raspberrypi.org/es-LA/projects/raspberry-pi-setting-up/0.

2. Set a Routed Wireless Access Point in the Raspberry Pi:

   https://www.raspberrypi.com/documentation/computers/configuration.html#setting-up-a-routed-wireless-access-point


3. With this done download the dependencies of the project in the Raspberry Pi. ("**./setup.sh**" can be used to download docker and git and at the end run the command "**sudo usermod -aG docker $USER**" to give permissions to docker to run without needing authorization from admin.)

4. Flash the ESP-32 with ussing the SSID of the Raspberry's Wireless Access Point name and password. Also `SESP_IPV4_ADDR` should be the IP address of the Raspberry and `ESP_FLASH_INTERNAL_IP` should be the IP of the computer you are flashing the ESP with.

5. With that done plug in the ESP into a power source near the Raspberry and after a few second press the restart button, the ESP should be set up to transmit data to the Raspberry.

6. Finally on the Raspberry, run only the services db, server and Adminer with the following command:
      
   To build the containers: **docker compose -f docker-compose.prod.yml build**
   To run the server: **docker compose -f docker-compose.prod.yml up**

7. Go to http://localhost:8000/ to view the database in Adminer.

