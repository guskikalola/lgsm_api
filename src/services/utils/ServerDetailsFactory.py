from services.domain import Server
from models.ServerDetailsModel import *


class ServerDetailsFactory:
    @staticmethod
    def build(server: Server, details: dict):
        baseInfo = {
            "ip_address": details.get("Internet IP"),
        }
        match(server.game_name):
            case "gmodserver":
                return GModDetailsModel(
                    **baseInfo,
                    server_version=details.get("Server Version"),
                    players=details.get("Players"),
                    current_map=details.get("Current map"),
                    game_mode=details.get("Game mode")
                )
            case _:
                return ServerDetailsModel(
                    **baseInfo
                )
