from pydantic import BaseModel, ConfigDict, Field, PrivateAttr
from pydantic_core.core_schema import ValidationInfo
from pydantic import ValidationError, field_validator
from typing import Optional
import datetime
import os
from dotenv import load_dotenv


"""
REQUIREMENT: Inheritance.
Note to instructors: This was previously commited on 3/16 but misidentified the requirement
as Validation, Encapsulation, and Polymorphism. 

These pydantic data classes inherit BaseModel from the pydantic library, 
sub classes of the BaseModel inherit the fields from their parent. Ex. UserCreate inherits
password field, used_code, and invite_code.
"""
################
##    USER    ##
################

class UserBase(BaseModel):
    name: Optional[str] = None
    password: Optional[str] = None
    used_code: bool = Field(
        default=False,
        description="Boolean: User used invite code."
    )
    invite_code: Optional[str] = Field(
        default=None,
        description="If used invite code, temporarily store."
    )

    _is_temp_user: bool = PrivateAttr(default=False)
    
    def set_is_temp(self, invite_key: str):
        self._is_temp_user = invite_key == os.getenv("DEV-INVITE-CODE")
    
    def get_is_temp(self) -> bool:
        return self._is_temp_user


class UserCreate(UserBase):
    name: str = Field(
        ..., 
        min_length=3, max_length=24,
        strict=True, 
        description = "Required 3-24 characters."
    )

    create_date: datetime.date = Field(
        default_factory=datetime.date.today
    )

    password1: str
    password2: str
    
    """
    Server-side enforcement of input validation when creating an account.
    """

    @field_validator('password1')
    def password_complexity(cls, v):
        if len(v) < 3 or len(v) >= 24:
            raise ValueError('Password must be between 3-24 characters')
        if v.find(' ') >= 0:
            raise ValueError('Password must not contain spaces')
        return v

    @field_validator('password2')
    def passwords_match(cls, v, info: ValidationInfo):
        if 'password1' in info.data and v != info.data['password1']:
            raise ValueError('Passwords do not match')
        return v
    
    @field_validator('name')
    def no_name_whitespace(cls, v, info: ValidationInfo):
        if v.find(' ') >= 0:
            raise ValueError('Username cannot contain spaces')
        return v


class UserLogin(UserBase):
    name: str = Field(
    ..., 
    min_length=3, max_length=24,
    strict=True, 
    description = "Required 3-24 characters."
    )
    @field_validator('name')
    def no_name_whitespace(cls, v, info: ValidationInfo):
        if v.find(' ') >= 0:
            raise ValueError('Username cannot contain spaces')
        return v
    
    password: str = Field(
        ...,
        min_length=3,
        max_length=24,
        strict=True,
        description="Field for existing password"
    )
    @field_validator('password')
    def no_password_whitespace(cls, v, info: ValidationInfo):
        if v.find(' ') >= 0:
            raise ValueError('Invalid password')
        return v

# NOTE: model_config allows the response to pull data directly from ORM Model
class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


################
##   BUDGET   ##
################

class BudgetBase(BaseModel):
    user_id: int = Field(
        ...,
        description="FK: ID for the budget's user"
    )
    budget_name: str = Field(
        default="overall",
        min_length=3, max_length=25,
        description="Budget category name. Max characters: 25. Default: overall"
    )
    budget_amount: float = Field(
        default=0.0,
        description="Budget amount. 99999999.99 limit. Default: 0.0"
    )
    budget_remaining: Optional[float] = Field(
        default=None,
        description="Optional: Remaining budget calculated server-side"
    )

class BudgetInit(BudgetBase):
    pass

class BudgetNew(BudgetBase):
    budget_name: str = Field(
        ..., 
        min_length=3, max_length=25,
        description="User created budget name; cannot have duplicate names."
    )

class BudgetUpdate(BudgetBase):
    id: int = Field(
        ...,
        description="Surrogate PK of the budget row to update."
    )
    user_id: int = Field(
        ...,
        description="FK: ID for the budget's user (ownership check)."
    )
    budget_name: Optional[str] = Field(
        None,
        min_length=3, max_length=25,
        description="New category name. Omit to leave unchanged."
    )
    budget_amount: Optional[float] = Field(
        None,
        description="New budget amount. Omit to leave unchanged."
    )

class BudgetResponse(BudgetBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    budget_name: str
    budget_amount: float

class BudgetDelete(BaseModel):
    id: int = Field(
        ...,
        description="Surrogate PK of the budget row to delete."
    )
    user_id: int = Field(
        ...,
        description="FK: ID for the budget's user"
    )



################
##    KEYS    ##
################

class KeyBase(BaseModel):
    invite_key: str = Field(
        ...,
        min_length=9, max_length=9,
        description="User invitiation key (pydantic model)."
    )

class KeyValidate(KeyBase):
    pass

class KeyCreate(BaseModel):
    key_list: list[KeyBase]

class KeyResponse(KeyBase):
    model_config = ConfigDict(from_attributes=True)
    invite_key: Optional[str] = Field(
        None,
        description="If key exists, return key, else None"
    )
    isValid: bool


#################
## TRANSACTION ##
#################

class TransactionBase(BaseModel):
    user: Optional[int] = None
    amount: float
    category_id: int
    description: Optional[str] = None
    txn_date: datetime.date


class TransactionAdd(TransactionBase):
    amount: float = Field(
        ...,
        description="Add - [Required] Transaction amount"
    )
    category_id: int = Field(
        ...,
        description="Add - [Default: overall] Transaction category"
    )
    txn_date: datetime.date = Field(
        default_factory=datetime.date.today,
        description="Add [Default: Today] Transaction date."
    )

#TODO: Fix validation

class TransactionQuery(TransactionBase):
    txn_date: Optional[datetime.date] = Field(
        None,
        description="Query - Transaction description"
    )
    category_id: Optional[int] = Field(
        None,
        description = "Query - Transaction category"
    )
    #TODO: Fix this but don't break schema
    amount: Optional[str] = Field(
        None,
        description="Query - Transaction amount."
    )


class TransactionResponse(TransactionBase):
    model_config = ConfigDict(from_attributes=True)
    id: int

#TODO: Add a TransactionDelete Model
