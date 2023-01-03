#!/bin/bash

# Update ubuntu
apt update -y && apt upgrade -y

# Install python
apt install -y python3-pip

# Update pip tool
pip3 install --upgrade pip

# Install dependencies

# ----
# git : pulling tools for linuxgsm
# libmariadb3 and libmariadb-dev : connector for mariadb
# gcc : python dependencies compiling 
# curl: linuxgsm script
# bash: linuxgsm script
# wget: linuxgsm script
# ----

apt install -y git libmariadb3 libmariadb-dev gcc curl bash wget

# Setup docker 
apt install -y ca-certificates gnupg lsb-release
mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
apt update
apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Install python requirements

pip3 install -r ./requirements.txt