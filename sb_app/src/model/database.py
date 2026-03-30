import os
from sqlalchemy import URL, create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv


load_dotenv()

url_object = URL.create(
    "mysql+pymysql",
    username=os.getenv("DATABASE_USER"),
    password=os.getenv("DATABASE_PASSWORD"),
    host=os.getenv("DATABASE_HOST"),
    database=os.getenv("DATABASE_DATA")
)

data_engine = create_engine(url_object)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=data_engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


#TASK REQUIREMENT: Inheritance
class Base(DeclarativeBase):
    pass


def init_db():
    Base.metadata.create_all(bind=data_engine)