# main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from threading import Thread
from app.consumers.rabbit_consumer import start_consumer_thread
from app.api import incidents
from app.api import events
from app.api import messages
from app.database.mongodb import get_incidents_collection
from app.websocket.endpoints import websocket_endpoint

import logging
from typing import AsyncGenerator

# Настройка логгера
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def ensure_indexes():
    """Создает индексы в MongoDB при старте."""
    collection = get_incidents_collection()
    collection.create_index(
        [("host", 1), ("message", 1)],
        unique=True,
        name="host_message_unique"
    )
    logger.info("MongoDB индексы созданы")

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Управление жизненным циклом приложения."""
    # Startup
    ensure_indexes()
    rabbit_thread = Thread(target=start_consumer_thread, daemon=True)
    rabbit_thread.start()
    
    logger.info("Сервисы запущены")
    yield
    logger.info("Приложение завершает работу")

app = FastAPI(
    title="Incident Tracker",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Регистрируем WebSocket endpoint
app.add_api_websocket_route("/ws", websocket_endpoint)

# Подключение роутеров
app.include_router(incidents.router)
app.include_router(events.router)
app.include_router(messages.router)