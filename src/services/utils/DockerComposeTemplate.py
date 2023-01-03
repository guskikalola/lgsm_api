from os import environ
template = """
version: '3.4'
services:
  linuxgsm:
    image: "ghcr.io/gameservermanagers/linuxgsm-docker:latest"
    container_name: {server_name}
    environment:
        - GAMESERVER={game_name}
        - LGSM_GITHUBUSER=GameServerManagers
        - LGSM_GITHUBREPO=LinuxGSM
        - LGSM_GITHUBBRANCH=master
    volumes:
        - {servers_dir}/{server_name}/serverfiles:/home/linuxgsm/serverfiles
        - {servers_dir}/{server_name}/log:/home/linuxgsm/log
        - {servers_dir}/{server_name}/config-lgsm:/home/linuxgsm/lgsm/config-lgsm
    ports:
        - "27015:27015/tcp"
        - "27015:27015/udp"
        - "27020:27020/udp"
        - "27005:27005/udp"
    restart: unless-stopped
"""

def DockerComposeTemplate(server_name: str, game_name: str):
        servers_dir = ""
        return template.format(server_name=server_name, game_name=game_name,
        servers_dir=environ.get("SERVERS_DIR"))