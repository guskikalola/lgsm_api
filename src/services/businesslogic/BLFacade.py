from services.dataaccess import DataAccess
from datetime import datetime, timedelta
from os import environ
from passlib.context import CryptContext
from jose import JWTError, jwt
from models import UserModel, ServerWithDetailsModel, ServerModel
from jose import JWTError
from models import TokenDataModel
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, Depends, status
from services.domain import User
from services.exceptions import ServerNotFoundException, ContainerNotRunningException
from services.enums import ExecutionMethodEnum

# Authetication enabled?
AUTHENTICATION_ENABLED: bool = environ.get("AUTHENTICATION_ENABLED") or True

# TODO : Find a way to convert from true/false to True/False
if AUTHENTICATION_ENABLED == "true":
    AUTHENTICATION_ENABLED = True
if AUTHENTICATION_ENABLED == "false":
    AUTHENTICATION_ENABLED = False

AUTHENTICATION_DISABLED_USERNAME: str = "administrator"
AUTHENTICATION_DISABLED_USER: User = User(
    username=AUTHENTICATION_DISABLED_USERNAME,
    active=True,
    email="admin@local",
    full_name="Administrator",
    hashed_password="",
)

# Hashing configuration
SECRET_KEY = environ.get("HASHING_SECRET_KEY") or "changeme"
ALGORITHM = environ.get("HASHING_ALGORITHM") or "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = environ.get(
    "ACCESS_TOKEN_EXPIRE_MINUTES") or 30
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(ACCESS_TOKEN_EXPIRE_MINUTES)

if SECRET_KEY == "changeme":
    raise RuntimeError(
        "HASHING_SECRET_KEY not defined! Define it with the env vars")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# /token endpoint configuration
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/user/token", auto_error=AUTHENTICATION_ENABLED)


class BLFacade:

    __dataaccess: DataAccess | None = None

    @staticmethod
    def setDataaccess(dataaccess: DataAccess):
        BLFacade.__dataaccess = dataaccess

        if not AUTHENTICATION_ENABLED:
            print("""
                Authentication is disabled!
                Default user will be used ( username: administrator )
            """)
            # Create administrator user
            BLFacade.create_user(
                username=AUTHENTICATION_DISABLED_USER.username,
                active=AUTHENTICATION_DISABLED_USER.active,
                full_name=AUTHENTICATION_DISABLED_USER.full_name,
                email=AUTHENTICATION_DISABLED_USER.email,
                password=""
            )

    @staticmethod
    def getDB() -> DataAccess:
        if BLFacade.__dataaccess is None:
            raise RuntimeError("DB dependency not injected into facade")
        return BLFacade.__dataaccess

    @staticmethod
    def get_user(username: str):
        db = BLFacade.getDB()
        db.open()
        user = db.get_user(username)
        db.close()
        return user

    @staticmethod
    def hash_password(password: str):
        return pwd_context.hash(password)

    @staticmethod
    def create_user(username: str, password: str, full_name: str = "", email: str = "", active: bool = True):
        db = BLFacade.getDB()
        db.open()
        hashed_password = BLFacade.hash_password(password)
        user = db.create_user(username=username, hashed_password=hashed_password,
                              full_name=full_name, email=email, active=active)
        db.close()
        return user

    @staticmethod
    def authenticate_user(username: str, plain_text_password: str):

        if AUTHENTICATION_ENABLED == False:
            return BLFacade.get_user(AUTHENTICATION_DISABLED_USERNAME)

        user = BLFacade.get_user(username)
        if not user:
            return False  # TODO: Handle not found error

        if user.password_correct(pwd_context, plain_text_password):
            return user
        else:
            return False

    @staticmethod
    def create_access_token(username: str):
        data = {
            "sub": username
        }

        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def decode_token(token: str):
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    @staticmethod
    def get_current_user(token: str = Depends(oauth2_scheme)):

        if AUTHENTICATION_ENABLED == False:
            return BLFacade.get_user(AUTHENTICATION_DISABLED_USERNAME).getModel()

        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = BLFacade.decode_token(token)
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
            token_data = TokenDataModel(username=username)
        except JWTError:
            raise credentials_exception
        user = BLFacade.get_user(token_data.username)
        if user is None:
            raise credentials_exception
        return user.getModel()

    @staticmethod
    def get_current_active_user(current_user: UserModel = Depends(get_current_user)):
        if not current_user.active:
            return False
        return current_user

    @staticmethod
    def create_server(server_name: str, game_name: str):
        """Create a new server

        Creates a new server entry in the database, creates the
        server folder and downloads the basic scripts from linuxgsm there.

        :param str server_name: Server unique identifier
        :param str game_name: Name of the server's game
        """

        db = BLFacade.getDB()
        db.open()
        # TODO : Handle duplicated key and invalid game
        try:
            server = db.create_server(server_name, game_name)
        except Exception as e:
            db.close()
            raise e
        else:
            db.close()
            server.download()
            return server

    @staticmethod
    def delete_server(server_name: str):
        db = BLFacade.getDB()
        db.open()
        server = db.delete_server(server_name)
        db.close()
        return server

    @staticmethod
    def get_server(server_name: str, with_details: bool = False) -> ServerModel | ServerWithDetailsModel:
        db = BLFacade.getDB()
        db.open()
        server = db.get_server(server_name)
        db.close()
        if with_details:
            return server.get_details_model()
        else:
            return server.get_model()

    @staticmethod
    def get_all_servers(with_details: bool) -> list[ServerModel] | list[ServerWithDetailsModel]:
        db = BLFacade.getDB()
        db.open()
        servers = db.get_all_servers()
        db.close()
        if with_details:
            return [server.get_details_model() for server in servers]
        else:
            return [server.get_model() for server in servers]

    @staticmethod
    def execute_method(server_name: str, execution_method: ExecutionMethodEnum, stop_container: bool):
        db = BLFacade.getDB()
        db.open()
        server = db.get_server(server_name)
        db.close()
        if server is None:
            raise ServerNotFoundException(f"Server not found. ({server_name})")

        match execution_method:
            case ExecutionMethodEnum.START:
                return server.start()
            case ExecutionMethodEnum.RESTART:
                return server.restart()
            case ExecutionMethodEnum.STOP:
                return server.stop(stop_container)
            case _:
                pass

    @staticmethod
    def get_details(server_name: str):
        db = BLFacade.getDB()
        db.open()
        server = db.get_server(server_name)
        db.close()

        if server is None:
            raise ServerNotFoundException(f"Server not found. ({server_name})")

        return server.get_details()

    @staticmethod
    def send_game_console_command(server_name: str, command: str):
        db = BLFacade.getDB()
        db.open()
        server = db.get_server(server_name)
        db.close()

        if server is None:
            raise ServerNotFoundException(f"Server not found. ({server_name})")

        return server.execute_game_command(command)
