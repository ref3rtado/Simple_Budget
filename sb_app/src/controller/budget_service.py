from fastapi import APIRouter, Depends, HTTPException, Cookie, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
from sqlalchemy.orm import Session
from src.model.database import get_db
from src.model.schema import BudgetNew, BudgetUpdate, BudgetDelete, BudgetResponse
from src.model import crud


router = APIRouter(prefix="/categories", tags=["b_service"])
templates = Jinja2Templates(directory="src/view/templates")


def _get_user_id(user_id: str = Cookie(default=None)) -> int:
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated.")
    return int(user_id)


def _render_rows(request: Request, uid: int, db: Session) -> HTMLResponse:
    """
    Switched to use Jinja Fragments instead of neededing extensive JScript
    Fetch budgets + surplus, render the category_rows fragment.
    """
    budgets = crud.get_budgets(uid, db)
    overall = next((b for b in budgets if b.budget_name == "overall"), None)
    cat_sum = sum(float(b.budget_amount) for b in budgets if b.budget_name != "overall")
    surplus = float(overall.budget_amount) - cat_sum if overall else 0.0
    return templates.TemplateResponse(
        "fragments/category_rows.html",
        {"request": request, "budgets": budgets, "surplus": surplus}
    )

"""
REQUIREMENT: Add, Modify, and Delete data
This service calls CRUD methods to add, update and delete budget categories.
"""

################
##    GET     ##
################

@router.get("/list", response_class=HTMLResponse)
def list_budgets(
    request: Request,
    uid: int = Depends(_get_user_id),
    db: Session = Depends(get_db)
):
    return _render_rows(request, uid, db)

@router.get("/dropdown", response_class=HTMLResponse)
def budget_dropdown(
    uid: int = Depends(_get_user_id),
    db: Session = Depends(get_db)
):
    """Returns <option> elements for the transaction form dropdown."""
    budgets = crud.get_budgets(uid, db)
    options = "".join(
        f'<option value="{b.id}">{b.budget_name.capitalize()}</option>'
        for b in budgets
    )
    return HTMLResponse(content=options)   

################
##    ADD     ##
################

@router.post("/add", response_class=HTMLResponse)
def add_category(
    request: Request,
    budget_name: str = Form(..., min_length=3, max_length=25),
    budget_amount: float = Form(default=0.0),
    uid: int = Depends(_get_user_id),
    db: Session = Depends(get_db)
):
    try:
        crud.add_budget(
            BudgetNew(user_id=uid, budget_name=budget_name, budget_amount=budget_amount),
            db
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
 
    return _render_rows(request, uid, db)


################
##   MODIFY   ##
################


@router.post("/update", response_class=HTMLResponse)
def update_category(
    request: Request,
    budget_id: int = Form(...),
    budget_name: str = Form(default=None, min_length=3, max_length=25),
    budget_amount: float = Form(default=None),
    uid: int = Depends(_get_user_id),
    db: Session = Depends(get_db)
):
    try:
        crud.update_budget(
            BudgetUpdate(
                id=budget_id,
                user_id=uid,
                budget_name=budget_name,
                budget_amount=budget_amount
            ),
            db
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return _render_rows(request, uid, db)


@router.post("/maximize", response_class=HTMLResponse)
def maximize_category(
    request: Request,
    budget_id: int = Form(...),
    uid: int = Depends(_get_user_id),
    db: Session = Depends(get_db)
):
    budgets = crud.get_budgets(uid, db)
    overall = next((b for b in budgets if b.budget_name == "overall"), None)
    cat_sum = sum(float(b.budget_amount) for b in budgets if b.budget_name != "overall")
    surplus = float(overall.budget_amount) - cat_sum if overall else 0.0
 
    if surplus <= 0:
        return _render_rows(request, uid, db)
 
    target = next((b for b in budgets if b.id == budget_id), None)
    if not target:
        raise HTTPException(status_code=404, detail="Category not found.")
 
    try:
        crud.update_budget(
            BudgetUpdate(
                id=budget_id,
                user_id=uid,
                budget_amount=float(target.budget_amount) + surplus
            ),
            db
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return _render_rows(request, uid, db)


################
##   DELETE   ##
################


@router.post("/delete", response_class=HTMLResponse)
def delete_category(
    request: Request,
    budget_id: int = Form(...),
    uid: int = Depends(_get_user_id),
    db: Session = Depends(get_db)
):
    try:
        crud.delete_budget(BudgetDelete(id=budget_id, user_id=uid), db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return _render_rows(request, uid, db)