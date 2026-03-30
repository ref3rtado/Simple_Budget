from fastapi import APIRouter, Depends, HTTPException, Cookie, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from src.model.database import get_db
from src.model import crud
from datetime import datetime
from typing import List, Optional


router = APIRouter(prefix="/report", tags=["r_service"])
templates = Jinja2Templates(directory="src/view/templates")


def _get_user_id(user_id: str = Cookie(default=None)) -> int:
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated.")
    return int(user_id)


def _render_report_rows(
    request: Request,
    uid: int,
    db: Session,
    date_filter: str | None = None,
    category_ids: list[int] | None = None,
    cost_filter: str | None = None,
) -> HTMLResponse:
    transactions = crud.query_transactions(
        user_id=uid,
        db=db,
        date_filter=date_filter,
        category_ids=category_ids,
        cost_filter=cost_filter,
    )
    budgets = crud.get_budgets(uid, db)
    report_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    budget_map = {b.id: b.budget_name for b in budgets}

    return templates.TemplateResponse(
        "fragments/report_rows.html",
        {
            "request": request,
            "transactions": transactions,
            "budget_map": budget_map,
            "report_date": report_datetime,
        },
    )

@router.get("/", response_class=HTMLResponse)
def report_page(
        request: Request,
    uid: int = Depends(_get_user_id),
    db: Session = Depends(get_db)
):
    budgets = crud.get_budgets(uid, db)
    return templates.TemplateResponse(
        "report.html",
        {"request": request, "budgets": budgets},
    )

@router.post("/filter", response_class=HTMLResponse)
def filter_transactions(
    request: Request,
    date_filter: Optional[str] = Form(default=None),
    category_ids: Optional[List[int]] = Form(default=None),
    cost_filter: Optional[str] = Form(default=None),
    uid: int = Depends(_get_user_id),
    db: Session = Depends(get_db)
):
    return _render_report_rows(request, uid, db, date_filter, category_ids, cost_filter)