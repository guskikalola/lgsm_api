# LinuxGSM CLI API

(!) This project is under development, its not usable yet and is more a proof of concept than an usable tool.

This is an API developed to interact with the LinuxGSM CLI through the web.
This project is not affiliated to the LinuxGSM team. Check their project at: https://linuxgsm.com/

This API is built using FastAPI and is designed to be run on a Docker container.

## Current features:

### Server

- [x] Create server
- [x] Delete server
- [x] Start/Stop/Restart server
- [x] Get server status
- [x] View server game console
- [x] Send commands to server game console
- [ ] Get server details

### Auth

- [x] Create user
- [x] Login as user
- [ ] User permissions 

### Misc

- [x] Get available games in linuxgsm

You can find the frontend implementation and docker-compose files at: https://github.com/guskikalola/lgsm_webpanel
