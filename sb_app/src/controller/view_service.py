from fastapi import APIRouter, Request, Cookie, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from src.model.database import get_db
from src.model import crud
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

load_dotenv()


router = APIRouter(tags=["views"])
templates = Jinja2Templates(directory="src/view/templates")


# EXAM REQUIREMENT: Validation.
# This dependency forces the user the either create an account or login,
# making them interact with the forms that include input validation.
def require_auth(user_id: str = Cookie(default=None)):
    if not user_id:
        return RedirectResponse(url="/", status_code=302)


@router.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse({"request": request}, "index.html")


@router.get("/new_user", response_class=HTMLResponse)
def new_user_page(request: Request):
    return templates.TemplateResponse({"request": request}, "new_user.html")


# EXAM REQUIREMENT: Validation.
# The injected depenency checks if user previously authorized. If they manually
# entered {url..}/dashboard, it will redirect to the login page.
@router.get("/dashboard0", response_class=HTMLResponse)
def get_new_dashboard(
    request: Request,
    auth=Depends(require_auth),
    db: Session = Depends(get_db),
    user_id: str = Cookie(default=None)
):
    if isinstance(auth, RedirectResponse):
        return auth
    is_temp_user = False
    if user_id:
        user = crud.get_user_by_id(int(user_id), db)
        if user and user.invite_code == os.getenv("DEV-INVITE-CODE"):
            is_temp_user = True
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "new_user": True, "is_temp_user": is_temp_user}
        )

@router.get("/dashboard", response_class=HTMLResponse)
def get_dashboard(request: Request,
    auth=Depends(require_auth),
    db: Session = Depends(get_db),
    user_id: str = Cookie(default=None)
):
    if isinstance(auth, RedirectResponse):
        return auth
    budgets = crud.get_budgets(int(user_id), db)
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "new_user": False, "budgets": budgets} 
        )


@router.get("/categories", response_class=HTMLResponse)
def categories_page(
    request: Request,
    auth=Depends(require_auth),
    user_id: str = Cookie(default=None)
):
    if isinstance(auth, RedirectResponse):
        return auth
    return templates.TemplateResponse(
        "categories.html",
        {"request": request, "user_id": user_id}
    )




