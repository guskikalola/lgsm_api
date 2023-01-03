from pydantic import BaseModel

class UserModel(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    active: bool = True

class UserModelPassword(UserModel):
    password: str