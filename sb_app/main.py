import uvicorn
import os
from datetime import timedelta
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starsessions import CookieStore
from starsessions import SessionMiddleware, SessionAutoloadMiddleware
from contextlib import asynccontextmanager
from src.controller.transaction_service import router as t_service
from src.controller.user_service import router as u_service
from src.controller.view_service import router as view_service
from src.controller.budget_service import router as b_service
from src.controller.report_service import router as r_service
from src.model import orm_models
from src.model.database import init_db


@asynccontextmanager
async def startup(app: FastAPI):
    init_db()
    yield

app = FastAPI(lifespan=startup)

IS_DEV = os.getenv("APP_ENV", "production").lower() == "development"

SESSION_SECRET = os.getenv("SESSION_SECRET")
if not SESSION_SECRET:
    raise RuntimeError("SESSION_SECRET is not set")

session_store = CookieStore(secret_key=SESSION_SECRET) 

app.add_middleware(SessionAutoloadMiddleware)
app.add_middleware(
    SessionMiddleware,
    store=session_store,
    lifetime=timedelta(minutes=15),
    cookie_https_only=not IS_DEV
)
app.mount("/static", StaticFiles(directory="src/view/static"), name="static")
app.include_router(view_service)
app.include_router(t_service)
app.include_router(u_service)
app.include_router(b_service)
app.include_router(r_service)

if __name__ == "__main__":
    # Used for debugging
    uvicorn.run(app, host="0.0.0.0", port=8000)
