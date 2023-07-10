# IoT Project - Communication between Raspberry Pi and ESP-32

---

# Project Overview

This project implements the communication logic between an ESP-32 and a Raspberry Pi to transmit five distinct data structures using either WiFi or Bluetooth as a medium.

With the help of a Graphical User Interface (GUI) built in PyQt, you can manipulate various aspects of the communication between the two devices. These aspects include, but are not limited to, viewing different graphs, modifying communication protocols, or changing transport layers.

The following sections describe how to install the prerequisites, set up, and execute the project.


## Prerequisites

-   Docker Engine (or Docker Desktop) is required to run the Docker Compose configuration for this project.

    -   [Install Docker](https://docs.docker.com/desktop/)

-   Python PDM Package Manager

    -   [Install PDM](https://pdm.fming.dev/latest/#installation)

-   ESP-IDF

    -   [Install ESP-IDF](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/get-started/)

-   Python 3.9 or greater
    -   [Install Python](https://www.python.org/downloads/)

## Setup and Execution

1. Rename `.env.template` to `.env` and fill in the values for the environment variables, if needed.

### Build and flash esp-3d code

```bash
./run.sh idf <idf.py commands>
# For example:
./run.sh idf build flash monitor
```

Note: We use the command ./run.sh because environment variables are set before building and flashing the code, for everything to work properly.

Run the Raspberry Pi code

```bash
./run.sh rungui
```

This will start the database, install dependencies and run the GUI.
