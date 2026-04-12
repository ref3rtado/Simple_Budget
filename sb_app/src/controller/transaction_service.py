from fastapi import APIRouter, Depends, Cookie, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from src.model.database import get_db
from src.model.schema import TransactionAdd, TransactionQuery, TransactionResponse
from src.model import crud

router = APIRouter(prefix="/transactions", tags=["t_service"])
templates = Jinja2Templates(directory="src/view/templates/")


def _get_user_id(user_id: str = Cookie(default=None)) -> int:
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated.")
    return int(user_id)

def _refresh_dash(request: Request, uid: int, db:Session) -> HTMLResponse:
    budgets = crud.get_budgets(uid, db)
    return templates.TemplateResponse(
        "fragments/data_viz.html",
        {"request": request, "budgets": budgets}
    )

@router.post("/add", response_class=HTMLResponse)
async def add_transaction(
    request: Request,
    transaction: TransactionAdd,
    uid: int = Depends(_get_user_id),
    db: Session=Depends(get_db)
    ):
    transaction.user = uid
    crud.add_transaction(transaction, db)
    return _refresh_dash(request, uid, db)


@router.post("/test-post")
async def test_post(request: Request):
    body = await request.json()
    return {"ok": True}