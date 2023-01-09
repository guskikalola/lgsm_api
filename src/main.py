from os import environ
from fastapi import FastAPI
from routers import server, users
from services.dataaccess import DataAccess
from services.businesslogic import BLFacade
from fastapi.middleware.cors import CORSMiddleware

# Connect to database
db_user = environ.get("MARIADB_USER")
db_password = environ.get("MARIADB_PASSWORD")
db_host = environ.get("MARIADB_HOST")
db_database = environ.get("MARIADB_DATABASE")

dataAccess = DataAccess(db_user,db_password,db_host,db_database)

dataAccess.initialize_db()

BLFacade.setDataaccess(dataAccess)

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
