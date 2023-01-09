from pydantic import BaseModel, Field
from services.enums import ServerStatusEnum
from models import ServerInputModel

class ServerModel(ServerInputModel):
    server_pretty_name: str = Field(
        title="The name of the server",
        max_length=30,
        min_length=5
    )
    server_status: ServerStatusEnum = Field (
        title="Game server status"
    )
