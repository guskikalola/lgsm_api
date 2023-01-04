from fastapi import APIRouter, Depends, HTTPException, Request
from services.businesslogic import BLFacade
from services.domain import User
from models import ServerModel
from services.exceptions import ServerNameRepeatedException
from services.enums.LinuxGSMResponses import ServerCommandsResponse
from services.exceptions import ServerNotFoundException
from services.enums import ExecutionMethodEnum
from sse_starlette.sse import EventSourceResponse
from services.utils import ConsoleStream 

router = APIRouter()


@router.get("/")
async def get_all_servers():
    return BLFacade.get_all_servers()


@router.get("/{server_name}")
async def get_server(server_name: str):
    return BLFacade.get_server(server_name)


@router.post("/{server_name}/download")
async def install_server(server_name: str, current_user: User = Depends(BLFacade.get_current_active_user)):
    server = BLFacade.get_server(server_name)
    if not server is None:
        return server.download()
    else:
        raise HTTPException(status_code=400, detail=[{
            "msg": "Server not found"
        }])


@router.post("/{server_name}/install")
async def install_server(server_name: str, current_user: User = Depends(BLFacade.get_current_active_user)):
    server = BLFacade.get_server(server_name)
    if not server is None:
        return server.install()
    else:
        raise HTTPException(status_code=400, detail=[{
            "msg": "Server not found"
        }])


@router.get("/{server_name}/details")
async def get_server_details(server_name: str, current_user: User = Depends(BLFacade.get_current_active_user)):
    try:
        details = BLFacade.get_details(server_name)
    except ServerNotFoundException:
        raise HTTPException(status_code=400, detail=[{
            "msg": "Server not found"
        }])
    else:
        return details


@router.get("/{server_name}/console")
async def console_stream(server_name: str, request: Request):
    server = BLFacade.get_server(server_name)
    if not server is None:
        # event_generator = server.get_console_stream(request)
        event_generator = ConsoleStream(server,request)
        return EventSourceResponse(event_generator)
    else:
        raise HTTPException(status_code=400, detail=[{
            "msg": "Server not found"
        }])

@router.post("/{server_name}/{execution_method}")
async def execute_method(server_name: str, execution_method: ExecutionMethodEnum, stop_container: bool = False, current_user: User = Depends(BLFacade.get_current_active_user)):
    try:
        rc = BLFacade.execute_method(
            server_name, execution_method, stop_container)
    except ServerNotFoundException:
        raise HTTPException(status_code=400, detail=[{
            "msg": "Server not found"
        }])
    else:
        if rc == ServerCommandsResponse.OK:
            return 200
        elif rc == ServerCommandsResponse.INFO or rc == ServerCommandsResponse.NOT_RUNNING:
            raise HTTPException(status_code=304, detail=[{
                "msg": f"Server not modified. Status code: {rc}"
            }])
        else:
            raise HTTPException(status_code=500, detail=[{
                "msg": f"Error while executing command. Status code: {rc}"
            }])


@router.delete("/{server_name}")
async def delete_server(server_name: str, current_user: User = Depends(BLFacade.get_current_active_user)):
    server = BLFacade.execute_method(server_name, "stop")

    server = BLFacade.delete_server(server_name)
    if not server is None:
        return server
    else:
        raise HTTPException(status_code=400, detail=[{
            "msg": "Server not found"
        }])


@router.post("/create")
async def create_server(server: ServerModel, current_user: User = Depends(BLFacade.get_current_active_user)):
    try:
        server = BLFacade.create_server(server.server_name, server.game_name)
    except ServerNameRepeatedException as e:
        raise HTTPException(status_code=400, detail=[{
            "msg": e.args[0]
        }])
    else:
        return server
