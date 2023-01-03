from fastapi import APIRouter
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from services.businesslogic.BLFacade import BLFacade
from services.domain.User import User
from models.UserModel import UserModelPassword
router = APIRouter()

@router.post("/register")
async def create_user(user: UserModelPassword):
    if user.username == "me":
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid username.")
    result = BLFacade.create_user(
        username=user.username, password=user.password, full_name=user.full_name, email=user.email, active=True)
    # TODO : Handle different error types ( user already exists, 500... )
    if isinstance(result, User):
        return result.getModel()
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Internal Server Error ( DB )")


@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = BLFacade.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = BLFacade.create_access_token(user.username)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me")
async def read_current_user(current_user: User = Depends(BLFacade.get_current_active_user)):
    if not current_user:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@router.get("/{username}")
async def get_user(username: str):
    user = BLFacade.get_user(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User not in database")
    else:
        return user.getModel()
