#!/bin/bash

# Update alpine

apk update && apk upgrade

# Install dependencies

# ----
# git : pulling tools for linuxgsm
# mariadb-connector-c-dev : connector for mariadb
# gcc : python dependencies compiling 
# curl : linuxgsm script
# bash : linuxgsm script
# wget : linuxgsm script
# musl-dev : stdlib.h
# ----

apk add git mariadb-connector-c-dev gcc curl bash wget musl-dev

# Setup docker 

apk add docker docker-cli-compose

# Install python requirements

pip3 install -r ./requirements.txt