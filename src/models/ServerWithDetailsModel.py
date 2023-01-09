from pydantic import BaseModel, Field
from models import ServerModel, ServerDetailsModel

class ServerWithDetailsModel(ServerModel):
    details: ServerDetailsModel
