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
    restart: unless-stopped
"""

def DockerComposeTemplate(server_name: str, game_name: str):
        return template.format(server_name=server_name, game_name=game_name,
        servers_dir=environ.get("SERVERS_DIR"))