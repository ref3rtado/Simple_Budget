import pytest
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.model.database import Base
from src.model.orm_models import User, Budget
from src.model.schema import UserCreate, BudgetBase
from src.model.crud import add_user, add_budget

TEST_DB_URL = "sqlite:///:memory:"

@pytest.fixture
def db():
    #Setup
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

    #Teardown
    Base.metadata.drop_all(engine)


def test_bad_username(db):
    """
    Username contains whitespace, raise Value error.
    Username does not meet min length (3)
    Username exceeds max length (24)
    """
    bad_username = "white space"
    with pytest.raises(ValueError) as ws_err:
        new_user = UserCreate(
            name = bad_username,
            password1 = "password",
            password2 = "password"
        )
    assert "Username cannot contain spaces" in str(ws_err.value)

    bad_username = "ab"
    with pytest.raises(ValueError) as min_err:
        new_user = UserCreate(
            name = bad_username,
            password1 = "password",
            password2 = "password"
        )

    bad_username = "abcdefghijklmnopqrstuvwqyz1234546677"
    with pytest.raises(ValueError) as max_err:
        new_user = UserCreate(
            name = bad_username,
            password1 = "password",
            password2 = "password"
        )


def test_bad_password(db):
    """
    Testing password mismatch
    Testing whitespace in password
    Testing password complexity
    """
    name = "TestUser"
    good_pw = "password"
    bad_pw = "password1"
    with pytest.raises(ValueError) as match_err:
        new_user = UserCreate(
            name = name,
            password1 = good_pw,
            password2 = bad_pw
        )
    assert "Passwords do not match" in str(match_err.value)

    bad_pw = "pass word"
    with pytest.raises(ValueError) as match_err:
        new_user = UserCreate(
            name = name,
            password1 = bad_pw,
            password2 = bad_pw
        )
    assert "Password must not contain spaces" in str(match_err.value)

    bad_pw = "pw"
    with pytest.raises(ValueError) as min_err:
        new_user = UserCreate(
            name = name,
            password1 = bad_pw,
            password2 = bad_pw
        )
    assert "Password must be between 3-24 characters" in str(min_err.value)

    bad_pw = "abcdefghijklmnopqrstuvwqyz1234546677"
    with pytest.raises(ValueError) as max_err:
        new_user = UserCreate(
            name = name,
            password1 = bad_pw,
            password2 = bad_pw
        )
    assert "Password must be between 3-24 characters" in str(max_err.value)