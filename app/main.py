from __future__ import annotations

from contextlib import AbstractAsyncContextManager, asynccontextmanager
from collections.abc import AsyncIterator, Callable

from aiormq.exceptions import AMQPError
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

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

    @app.exception_handler(AMQPError)
    async def amqp_error_handler(_: Request, __: AMQPError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": "message bus temporarily unavailable"},
        )

    app.include_router(api_router)
    return app


app = create_app()
