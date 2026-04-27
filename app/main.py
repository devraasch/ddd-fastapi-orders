from __future__ import annotations

from contextlib import AbstractAsyncContextManager, asynccontextmanager
from collections.abc import AsyncIterator, Callable

from fastapi import FastAPI

from app.infrastructure.database import models  # noqa: F401
from app.infrastructure.database.base import Base, engine
from app.infrastructure.messaging.rabbitmq_publisher import create_rabbitmq_publisher
from app.presentation.api.routes import router as api_router

Lifespan = Callable[[FastAPI], AbstractAsyncContextManager[None]]


@asynccontextmanager
async def production_lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Schema inicial sem migrations (MVP). Em produção, trocar por Alembic.
    Base.metadata.create_all(bind=engine)

    publisher, rabbit_cleanup = await create_rabbitmq_publisher()
    app.state.event_publisher = publisher

    yield

    await rabbit_cleanup()


@asynccontextmanager
async def noop_lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Lifespan vazio — usado em testes para não falar com Postgres/RabbitMQ."""
    yield


def create_app(
    *,
    lifespan: Lifespan | None = None,
) -> FastAPI:
    _lifespan = production_lifespan if lifespan is None else lifespan
    app = FastAPI(
        title="fastapi-ordering-ddd",
        lifespan=_lifespan,
    )
    app.include_router(api_router)
    return app


app = create_app()
