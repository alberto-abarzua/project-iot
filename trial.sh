#!/bin/bash
# Check if the distribution is Ubuntu-based
if grep -q "ubuntu" /etc/os-release; then
    echo "This is an Ubuntu-based distribution."
# Check if the distribution is Debian-based
elif grep -q "debian" /etc/os-release; then
    echo "This is a Debian-based distribution."
# If the distribution is neither Debian nor Ubuntu-based
else
    echo "This distribution is not supported."
    exit 1
fi