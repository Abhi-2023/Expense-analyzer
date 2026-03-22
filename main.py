from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from config import settings
from api.auth import router as auth_router
from pages.auth_pages import router as auth_pages_router
from api.upload import router as upload_router
from pages.upload_pages import router as upload_pages_router
from api.predict import router as predict_router
from api.dashboard import router as dashboard_router
from pages.dashboard_pages import router as dashboard_page_router
from pages.home import router as home_router

app = FastAPI()
app.mount("/static", StaticFiles(directory='static'), name='static')
app.include_router(auth_router)
app.include_router(auth_pages_router)
app.include_router(upload_router)
app.include_router(upload_pages_router)
app.include_router(predict_router)
app.include_router(dashboard_router)
app.include_router(dashboard_page_router)
app.include_router(home_router)


