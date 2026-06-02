from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes.tts import router as tts_router

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="MiMo V2.5 TTS Web API",
    description="FastAPI proxy for Xiaomi MiMo Token Plan TTS",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境建议改成你的前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tts_router, prefix="/api")

# 静态前端页面：访问 http://localhost:8000 即可打开
app.mount(
    "/",
    StaticFiles(directory=str(BASE_DIR / "static"), html=True),
    name="static",
)
