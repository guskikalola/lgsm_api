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

# Install python requirements

pip3 install -r ./requirements.txt

# Install linuxgsm script dependencies

dpkg --add-architecture i386
apt update -y
apt install -y curl wget file tar bzip2 gzip unzip bsdmainutils python3 util-linux ca-certificates binutils bc jq tmux netcat lib32gcc-s1 lib32stdc++6 libsdl2-2.0-0:i386 steamcmd telnet expect