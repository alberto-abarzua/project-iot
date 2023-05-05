# Base image
FROM espressif/idf:release-v5.1


# sudo apt-get install cppcheck
RUN apt-get update && apt-get install -y cppcheck 
  
COPY ./project/ /workspace/

COPY generate_kconfig.py /usr/local/bin/