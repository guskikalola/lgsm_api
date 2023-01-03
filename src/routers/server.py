from fastapi import APIRouter, Depends, HTTPException
from services.businesslogic.BLFacade import BLFacade
from services.domain.User import User
from models.ServerModel import ServerModel
from services.exceptions import ServerNameRepeatedException

router = APIRouter()


@router.get("/")
async def get_all_servers():
    return BLFacade.get_all_servers()


@router.get("/{server_name}")
async def get_server(server_name: str):
    return BLFacade.get_server(server_name)

@router.get("/{server_name}/install")
async def install_server(server_name: str, current_user: User = Depends(BLFacade.get_current_active_user)):
    server = BLFacade.get_server(server_name)
    server.install()

@router.delete("/{server_name}")
async def delete_server(server_name: str, current_user: User = Depends(BLFacade.get_current_active_user)):
    server = BLFacade.delete_server(server_name)
    if not server is None:
        return server
    else:
        raise HTTPException(status_code=400, detail=[{
            "msg": "Server not found"
        }])

@router.post("/")
async def create_server(server: ServerModel, current_user: User = Depends(BLFacade.get_current_active_user)):
    try:
        server = BLFacade.create_server(server.server_name,server.game_name)
    except ServerNameRepeatedException as e:
        raise HTTPException(status_code=400, detail=[{
            "msg": e.args[0]
        }])
    else:
        return server