from .database import Base
from sqlalchemy import Integer, String, Date, Numeric, ForeignKey, ForeignKeyConstraint
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import Mapped, mapped_column
import datetime
from decimal import Decimal
from typing import Optional


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(24), nullable=False, unique=True)
    create_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(60), nullable=False)
    invite_code: Mapped[str] = mapped_column(String(9), nullable=True)
    used_code: Mapped[bool] = mapped_column(nullable=False, default=False)


class Budget(Base):
    __tablename__ = "budget"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    budget_name: Mapped[str] = mapped_column(
        String(25), nullable=False, default="overall"
    )
    budget_amount: Mapped[Decimal] = mapped_column(Numeric, nullable=False)

    budget_remaining: Mapped[Decimal] = mapped_column(Numeric, nullable=True)


class Transaction(Base):
    __tablename__ = "transaction"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    transaction_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    cost: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    budget_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("budget.id", ondelete="SET NULL"), nullable=True
    )
    description: Mapped[Optional[str]] = mapped_column(String(25), nullable=True)


class InviteCode(Base):
    __tablename__ = "invite_key"

    invite_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    invite_code: Mapped[str] = mapped_column(String(9), name="code", nullable=False)


class Test(Base):
    __tablename__ = "test"

    ID: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    Message: Mapped[str] = mapped_column(String(100), nullable=False)
