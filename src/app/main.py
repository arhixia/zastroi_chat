from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.api.auth.auth import router as auth_router
from app.api.admin import router as admin_router
from app.api.sites import router as sites_router
from app.api.widget import router as widget_router
 



app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")
app.include_router(sites_router, prefix="/api/v1")
app.include_router(widget_router, prefix="/api/v1")
 
WIDGET_JS_PATH = Path(__file__).resolve().parent / "static" / "widget.js"
 
 
@app.get("/widget.js")
async def widget_js():
    """Раздаём сам файл виджета — на него ссылается сгенерированный код установки."""
    return FileResponse(WIDGET_JS_PATH, media_type="application/javascript")


@app.get("/health")
async def health():
    return {"status": "ok"}

