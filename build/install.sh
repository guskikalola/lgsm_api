#!/bin/bash

# Update alpine

apk update && apk upgrade

# Install dependencies

# ----
# mariadb-connector-c-dev : connector for mariadb
# gcc : python dependencies compiling 
# musl-dev : stdlib.h
# ----

apk add --no-cache mariadb-connector-c-dev gcc musl-dev

# Setup docker 

apk add --no-cache docker-cli docker-cli-compose

# Install python requirements

pip3 install -r ./requirements.txt

# Remove packages used for building
apk del gcc