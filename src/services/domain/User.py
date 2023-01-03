from models.UserModel import UserModel
from passlib.context import CryptContext


class User:
    def __init__(self, username: str, hashed_password: str, active: bool, email: str = "", full_name: str = ""):
        self.username = username
        self.hashed_password = hashed_password
        self.active = active
        self.email = email
        self.full_name = full_name

    def password_correct(self,ctx: CryptContext, password: str):
        return ctx.verify(password, self.hashed_password)

    def getModel(self):
        return UserModel(
            username=self.username,
            email=self.email,
            full_name=self.full_name,
            active=self.active
        )
