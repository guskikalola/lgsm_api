from pydantic import BaseModel, Field

class ServerDetailsModel(BaseModel):
    ip_address: str | None = Field(
        title="Server IP address",
    )