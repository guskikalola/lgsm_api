from pydantic import BaseModel, Field
from services.enums import ServerStatusEnum

class ServerInputModel(BaseModel):
    server_name: str = Field(
        title="The server identifier",
        max_length=50,
        min_length=5
    )
    game_name: str = Field(
        title="The name of the game",
        max_length=50,
        min_length=5
    )
