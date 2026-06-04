from fastapi import APIRouter, Depends, Response, HTTPException, Request, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import ValidationError
from sqlalchemy.orm import Session
from src.model.database import get_db
from src.model.schema import UserBase, UserCreate, UserResponse, UserLogin
from src.model.schema import BudgetInit, BudgetNew, BudgetUpdate, BudgetResponse
from src.model.schema import KeyResponse, KeyValidate
from src.model import crud
import json
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/user", tags=["u_service"])

"""
EXAM REQUIREMENT: Polymorphism. crud.add_user returns an ORM User object, which is converted
                  to a Pydantic model (UserResponse), which is then used to construct the json response.
                  Additionally, the browser cookie stores the user_id as a string which is type casted
                  from the UserCreate object's id value. 
"""
@router.post("/add_user", response_model=UserResponse)
def add_new_user(user: UserCreate, response: Response, db: Session = Depends(get_db)):
    new_user = crud.add_user(user, db)
    default_budget = BudgetInit(user_id=new_user.id)
    crud.add_budget(default_budget, db)
    response.set_cookie(key="user_id", value=str(new_user.id), httponly=True)
    response.headers["HX-Redirect"] = "/dashboard0"
    return new_user


@router.post("/check_invite", response_model=KeyResponse)
def check_invite(key: KeyValidate, response: Response, db: Session = Depends(get_db)):
    result = crud.check_invite_code(key, db)
    if not result.isValid:
        raise HTTPException(status_code=400, detail="Invalid key")
    # Dev invite code: skip account creation and auto-create a temp user instead.
    if key.invite_key == os.getenv("DEV-INVITE-CODE"):
        response.headers["HX-Redirect"] = "/user/create_temp_user"
        return result
    response.headers["HX-Trigger"] = json.dumps({"keyValid": {"invite_key": key.invite_key}})
    return result


@router.post("/create_temp_user")
def create_temp_user(response: Response, db: Session = Depends(get_db)):
    """Auto-create a temporary demo account and redirect straight to the dashboard."""
    user = crud.add_temp_user(db)
    default_budget = BudgetInit(user_id=user.id)
    crud.add_budget(default_budget, db)
    response.set_cookie(key="user_id", value=str(user.id), httponly=True)
    response.headers["HX-Redirect"] = "/dashboard0"
    return None

@router.post("/login", response_model=UserResponse)
def login_user(user: UserLogin, response: Response, db: Session = Depends(get_db)):
    success = crud.login_user(user, db)
    if not success:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    response.set_cookie(key="user_id", value=str(success.id), httponly=True)
    response.headers["HX-Redirect"] = "/dashboard"
    return success


@router.post("/logout", response_model=None)
def logout_user(response: Response, db: Session = Depends(get_db), user_id: str = Cookie(default=None)):
    # If the active user is a temp/demo account, delete them before clearing the cookie.
    if user_id:
        dev_code = os.getenv("DEV-INVITE-CODE")
        user = crud.get_user_by_id(int(user_id), db)
        if user and user.invite_code == dev_code:
            crud.delete_user(int(user_id), db)
    response.delete_cookie(key="user_id")
    response.headers["HX-Redirect"] = "/"
    return None

@router.post("/edit_budget", response_model=BudgetResponse)
def edit_budget(budget: BudgetNew, db: Session = Depends(get_db)):
    return crud.add_budget(budget, db)

