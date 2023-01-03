from pydantic import BaseModel, Field


class ServerModel(BaseModel):
    server_name: str = Field(
        title="The name of the server",
        max_length=30,
        min_length=5
    )
    game_name: str = Field(
        title="The name of the game",
        max_length=30,
        min_length=5
    )
