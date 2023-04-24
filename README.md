# Project IoT - Communication between Raspberry Pi and ESP-32

---



## Requirements

- Install Docker Engine (or Desktop) to run docker compose of project.

- Rename `.env.template` to `.env`

## How tu run

* Set in the `.env` file variable `ESP_DEVICE` to the port that the ESP-32 is connected to
  * Ej: `ESP_DEVICE=/dev/ttyUSB0` 
* To run build monitor flash, and run the servers all at the same time
  * `sudo ./run.sh`  
  * We need sudo to access the port where the ESP-32 is connected on the host computer

