# resources uses: https://www.starlette.dev/middleware/

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from db import create_db_and_tables
from routes.admin import router as admin_router
from routes.dashboard import router as dashboard_router
from routes.ingestion import router as ingestion_router
from routes.login import router as login_router
from routes.test_db import router as test_db_router
from routes.latest_reading import router as latest_reading_router
from routes.devices import router as devices_router
from routes.accounts import router as accounts_router
from routes.tasks import router as tasks_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    SessionMiddleware,
    secret_key="this is a long secret key that needs to be replaced"
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(login_router)
app.include_router(dashboard_router)
app.include_router(admin_router)
app.include_router(ingestion_router)
app.include_router(test_db_router)
app.include_router(latest_reading_router)
app.include_router(devices_router)
app.include_router(accounts_router)
app.include_router(tasks_router)