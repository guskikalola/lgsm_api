from pydantic import BaseModel, Field


class ServerDetailsModel(BaseModel):
    ip_address: str | None = Field(
        title="Server IP address",
    )


class GModDetailsModel(ServerDetailsModel):
    server_version: str | None = Field(
        title="GMod server's version"
    )
    players: str | None = Field(
        title="Players amount",
    )
    current_map: str | None = Field(
        title="Currently playing map"
    )
    game_mode: str | None = Field(
        title="Currently playing gamemode"
    )
