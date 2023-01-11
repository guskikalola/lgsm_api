from os import environ,rename,path,stat
from fastapi import FastAPI
from routers import server, users, game
from services.dataaccess import DataAccess
from services.businesslogic import BLFacade
from fastapi.middleware.cors import CORSMiddleware
import logging
from datetime import datetime

LOGS_DIR="/app/logs"
CURRENT_LOGS_FILE=path.join(LOGS_DIR,"current.log")
TODAY = datetime.today()
OLD_LOGS_FILE_RENAME=path.join(LOGS_DIR,f"{TODAY.strftime('%Y-%m-%d')}.log")
ONE_DAY_IN_MS = 86400000

# Rename previous logs if they are from a different day
last_timestamp = stat(CURRENT_LOGS_FILE).st_ctime
today_timestamp =TODAY.timestamp()
last_is_old = (today_timestamp - last_timestamp) > ONE_DAY_IN_MS
if path.exists(CURRENT_LOGS_FILE) and last_is_old:
    rename(CURRENT_LOGS_FILE, OLD_LOGS_FILE_RENAME)

# Setup logging
logger = logging.getLogger("lgsm_api")
logging.basicConfig(
    filename=CURRENT_LOGS_FILE,
    format='%(asctime)s [%(levelname)s:%(name)s]: %(message)s',
    datefmt='%Y/%m/%d %I:%M:%S %p',
    level=logging.DEBUG,
)

logging.getLogger("sse_starlette.sse").disabled = True
logging.getLogger("passlib.handlers.bcrypt").disabled = True

# Connect to database
db_user = environ.get("MARIADB_USER")
db_password = environ.get("MARIADB_PASSWORD")
db_host = environ.get("MARIADB_HOST")
db_database = environ.get("MARIADB_DATABASE")

dataAccess = DataAccess(db_user,db_password,db_host,db_database)

dataAccess.initialize_db()

BLFacade.setDataaccess(dataAccess)
BLFacade.load_game_list()

# Create application
app = FastAPI(redoc_url=None)

# Setup CORS
origins = [
    "http://localhost:3000",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    server.router,
    prefix="/api/v1/server",
    tags= ["servers"]
    )
app.include_router(
    users.router,
    prefix="/api/v1/user",
    tags= ["users"]
    )
app.include_router(
    game.router,
    prefix="/api/v1/game",
    tags= ["games"]
    )
