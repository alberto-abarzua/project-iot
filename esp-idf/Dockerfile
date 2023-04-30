# Base image
FROM espressif/idf:release-v4.4

# Install Python
RUN apt-get update && apt-get install -y python3


# Copy the entire project directory
# COPY project/ /workspace/

# Copy the Python script
COPY generate_kconfig.py /usr/local/bin/