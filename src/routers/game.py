from fastapi import APIRouter
from fastapi import Depends, HTTPException, status
from services.businesslogic.BLFacade import BLFacade
from models import GameModel
router = APIRouter()

@router.get("/", response_model=list[GameModel])
def get_all_games():
    return BLFacade.get_game_list()