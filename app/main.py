from __future__ import annotations

from contextlib import AbstractAsyncContextManager, asynccontextmanager
from collections.abc import AsyncIterator, Callable

from fastapi import FastAPI

from app.infrastructure.messaging.rabbitmq_publisher import create_rabbitmq_publisher
from app.presentation.api.routes import router as api_router

Lifespan = Callable[[FastAPI], AbstractAsyncContextManager[None]]


@asynccontextmanager
async def production_lifespan(app: FastAPI) -> AsyncIterator[None]:
    publisher, rabbit_cleanup = await create_rabbitmq_publisher()
    app.state.event_publisher = publisher

    yield

    await rabbit_cleanup()


@asynccontextmanager
async def noop_lifespan(app: FastAPI) -> AsyncIterator[None]:
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
