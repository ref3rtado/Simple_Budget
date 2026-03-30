import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
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

app.mount("/static", StaticFiles(directory="src/view/static"), name="static")

app.include_router(view_service)
app.include_router(t_service)
app.include_router(u_service)
app.include_router(b_service)
app.include_router(r_service)

if __name__ == "__main__":
    # Used for debugging
    uvicorn.run(app, host="0.0.0.0", port=8000)
