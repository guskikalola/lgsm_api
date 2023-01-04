from pydantic import BaseModel, Field

class GameConsoleCommand(BaseModel):
    command: str = Field(
        title="Server IP address",
        max_length=1000
    )
