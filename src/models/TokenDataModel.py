from pydantic import BaseModel


class TokenDataModel(BaseModel):
    username: str | None = None