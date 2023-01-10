from pydantic import BaseModel, Field

class GameModel(BaseModel):
    gm: str = Field(
        title="Game simple name",
    )
    game_name: str = Field(
        title="Game identifier"
    )
    game_full_name: str = Field(
        title="Game full name"
    )
