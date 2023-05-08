# IoT Project - Communication between Raspberry Pi and ESP-32

---

## Prerequisites

- Install Docker Engine (or Desktop) to run the Docker Compose configuration for this project.
- Python 3
- Python PDM version 2.5.5

## Setup and Execution

1. Rename the `.env.template` file to `.env`.

2. Most of the variables in the `.env` file can be left unchanged for the project to work. However, you need to set the following required variables:
   - `SESP_IPV4_ADDR`: The IP address that the ESP will target (IP of the Python server).
   - `ESP_DEVICE_PORT`: The USB port to which the ESP is connected for flashing and monitoring.

3. To build, flash, and monitor the ESP-32, as well as run the servers simultaneously, execute the following command:
