from sqlalchemy.orm import Session
from sqlalchemy import select, func
from .orm_models import Test, User, Budget, Transaction, InviteCode
from .schema import UserBase, UserCreate, UserLogin
from .schema import BudgetBase, BudgetNew, BudgetUpdate, BudgetDelete
from .schema import KeyBase, KeyCreate, KeyValidate, KeyResponse
from .schema  import TransactionAdd, TransactionQuery, TransactionResponse
import bcrypt
import os
from dotenv import load_dotenv
import datetime
from decimal import Decimal
from .SENDER import SENDER


"""
REQUIREMENT: Add, Modify, and Delete data
This script now allows the user to perform MySQL INSERT, UPDATE, and DELETE data
db == Session obj
INSERT == db.add(value) | commit
UDPATE == row = select(ORM_Model) | row.col = new_value | commit
DELETE ==  db.delete(row) | commit
"""

################
##    USER    ##
################

def delete_user(user_id: int, db: Session) -> None:
    """Hard-delete a user by PK. Cascades remove their budgets and transactions."""
    row = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
    if row:
        db.delete(row)
        db.commit()


def get_user_by_id(user_id: int, db: Session) -> User | None:
    """Return a User row by PK, or None if not found."""
    return db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()


def add_temp_user(db: Session) -> User:
    """Create a temporary demo user with an auto-incremented name (tempuser1, tempuser2, …).

    The invite_code is intentionally kept on the record so that logout can
    detect it and trigger account deletion.
    """
    load_dotenv()
    count = db.execute(
        select(func.count()).where(User.name.like("tempuser%"))
    ).scalar()
    temp_name = f"tempuser{count + 1}"
    password_bytes = "p@ssW0rd".encode("utf-8")
    hashed_password = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    row = User(
        name=temp_name,
        create_date=datetime.date.today(),
        password_hash=hashed_password,
        invite_code=os.getenv("DEV-INVITE-CODE"),
        used_code=True,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


#TODO: Retured UserResponse shoud login, then remove the key from both tables.
def add_user(new_user: UserCreate, db: Session) -> User:
    password_bytes = new_user.password1.encode("utf-8")
    hashed_password = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    row = User(
        name=new_user.name,
        create_date=new_user.create_date,
        password_hash=hashed_password,
        invite_code=new_user.invite_code,
        used_code=new_user.used_code
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


#NOTE: remove_code won't remove dev key.
#TODO: Implement the temp account functionality (Not needed for exam)
def login_user(user: UserLogin, db: Session) -> User:
    password_bytes = user.password.encode("utf-8")
    db_user = db.execute(
        select(User).where(user.name == User.name)
    ).scalar_one_or_none()
    if db_user and bcrypt.checkpw(
        password_bytes,
        db_user.password_hash.encode('utf-8')
    ):
        if db_user.invite_code and db_user.used_code:
            remove_code(db_user, db)
            db_user.invite_code = None
            db.commit()
        return db_user
    else:
        return None


################
##   BUDGET   ##
################

def _name_taken(user_id: int, budget_name: str, db: Session, exclude_id: int = None) -> bool:
    """Return True if budget_name already exists for this user.
    Optionally exclude a specific row id (used during update to ignore self).
    """
    query = select(func.count()).where(
        Budget.user_id == user_id,
        Budget.budget_name == budget_name
    )
    if exclude_id is not None:
        query = query.where(Budget.id != exclude_id)
    return db.execute(query).scalar() > 0


def add_budget(budget: BudgetBase, db: Session) -> Budget:
    if _name_taken(budget.user_id, budget.budget_name, db):
        raise ValueError(
            f"A budget category named '{budget.budget_name}' already exists."
        )
    row = Budget(
        user_id=budget.user_id,
        budget_name=budget.budget_name,
        budget_amount=budget.budget_amount,
        budget_remaining=budget.budget_amount
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def get_budgets(user_id: int, db: Session) -> list[Budget]:
    """Return all budget rows for a user, 'overall' row first."""
    return db.execute(
        select(Budget)
        .where(Budget.user_id == user_id)
        .order_by(
            (Budget.budget_name != "overall"),
            Budget.budget_name
        )
    ).scalars().all()


def update_budget(payload: BudgetUpdate, db: Session, owner: SENDER=SENDER.OTHER) -> Budget:
    """Update name and/or amount for a budget row, located by surrogate id.

    Raises ValueError for:
      - Row not found or not owned by payload.user_id
      - Duplicate name for this user
      - Renaming the 'overall' row
      - Setting 'overall' amount below the sum of all other categories
    """
    row = db.execute(
        select(Budget).where(
            Budget.id == payload.id,
            Budget.user_id == payload.user_id
        )
    ).scalar_one_or_none()

    if row is None:
        raise ValueError("Budget category not found.")

    if payload.budget_name is not None:
        if row.budget_name == "overall":
            raise ValueError("The 'overall' budget category cannot be renamed.")
        if payload.budget_name != row.budget_name:
            if _name_taken(payload.user_id, payload.budget_name, db, exclude_id=row.id):
                raise ValueError(
                    f"A budget category named '{payload.budget_name}' already exists."
                )
        row.budget_name = payload.budget_name

    if payload.budget_amount is not None:
        #NOTE: Allowing user to go over budget and instead display message
        """
        TODO: Implement some logic to allow the user to decide if they want to 
        reset the budget_remaining value. There currently isn't a way to cycle 
        the budget_remaining value so to reset it you have to change the budget amount.
        """
        row.budget_amount = payload.budget_amount
        if payload.budget_remaining is None: 
            row.budget_remaining = payload.budget_amount
    
    #NOTE: 3/19 : Called from add_transaction
    if payload.budget_remaining is not None:
        row.budget_remaining -= Decimal(str(payload.budget_remaining))

    if (row.budget_name != 'overall') and (owner is SENDER.ADD_TRANSACTION):
        overall_row = db.execute(select(Budget)
            .where(Budget.user_id == row.user_id,Budget.budget_name == 'overall')
            ).scalar_one_or_none()
        overall_row.budget_remaining -= Decimal(str(payload.budget_remaining))

    db.commit()
    db.refresh(row)

    if (row.budget_name != 'overall') and (owner is SENDER.ADD_TRANSACTION):
        db.refresh(overall_row)
    
    return row


def delete_budget(payload: BudgetDelete, db: Session) -> bool:
    """
    Delete a budget row by surrogate id.
    """
    row = db.execute(
        select(Budget).where(
            Budget.id == payload.id,
            Budget.user_id == payload.user_id
        )
    ).scalar_one_or_none()

    if row is None:
        raise ValueError("Budget category not found.")

    if row.budget_name == "overall":
        raise ValueError("The 'overall' budget category cannot be deleted.")

    db.delete(row)
    db.commit()
    return True


################
##    KEYS    ##
################

def add_invite_codes(keys: KeyCreate, db: Session) -> list[InviteCode]:
    added_codes = []
    for invite_key in keys.key_list:
        row = InviteCode(invite_code=invite_key.invite_key)
        db.add(row)
        db.commit()
        db.refresh(row)
        added_codes.append(row)
    return added_codes


def check_invite_code(invite_key: KeyValidate, db: Session) -> InviteCode:
    result = db.execute(
        select(InviteCode.invite_code).where(
            InviteCode.invite_code == invite_key.invite_key)
    ).scalar_one_or_none()
    if result:
        return KeyResponse(Key=result, isValid=True)
    return KeyResponse(invite_key=None, isValid=False)


def remove_code(user: User, db: Session) -> None:
    row_to_delete = db.execute(
        select(InviteCode).where(
            InviteCode.invite_code == user.invite_code)
    ).scalar_one()
    if row_to_delete.invite_code != os.getenv("DEV-INVITE-CODE"):
        db.delete(row_to_delete)
    user.invite_code = None


#################
## TRANSACTION ##
#################


def add_transaction(t: TransactionAdd, db: Session) -> Transaction:
    row = Transaction(
        transaction_date = t.txn_date,
        cost = t.amount,
        user_id = t.user,
        budget_id = t.category_id,
        description = t.description
    )
    try:
        db.add(row)
        db.commit()
    except Exception:
        #TODO: Find out what to raise
        print("Issues committing new transaction")
        pass
    else:
        db.refresh(row)
        update_budget(BudgetUpdate(
            id=row.budget_id,
            user_id=row.user_id,
            budget_remaining=row.cost),
            db, SENDER.ADD_TRANSACTION
            )

    return row

def query_transactions(
        user_id: int,
        db: Session,
        date_filter: str | None = None,
        category_ids: str | None = None,
        cost_filter: str | None = None
) -> list[Transaction]:
    query = select(Transaction).where(Transaction.user_id == user_id)

    if date_filter in ("7", "30"):
        cutoff = datetime.date.today() - datetime.timedelta(days=int(date_filter))
        query = query.where(Transaction.transaction_date >= cutoff)

    if category_ids:
        query =  query.where(Transaction.budget_id.in_(category_ids))

    match cost_filter:
        case ">100":
            query = query.where(Transaction.cost > 100)
        case ">50":
            query= query.where(Transaction.cost > 50)
        case "<50":
            query = query.where(Transaction.cost < 50)
        case _:
            pass
    
    query = query.order_by(Transaction.transaction_date.desc())
    return db.execute(query).scalars().all()
