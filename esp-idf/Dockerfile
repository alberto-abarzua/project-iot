# Base image
FROM espressif/idf:latest


# sudo apt-get install cppcheck
RUN apt-get update && apt-get install -y cppcheck 
  
COPY ./project/ /workspace/

COPY generate_kconfig.py /usr/local/bin/