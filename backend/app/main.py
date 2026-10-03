from fastapi import FastAPI

from backend.app.api.routes import router
from backend.app.core.config import APP_DESCRIPTION, APP_TITLE, APP_VERSION

app = FastAPI(
    title=APP_TITLE,
    version=APP_VERSION,
    description=APP_DESCRIPTION,
)

app.include_router(router)
