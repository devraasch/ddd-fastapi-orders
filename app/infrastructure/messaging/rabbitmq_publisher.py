import asyncio
import json
import logging
from collections.abc import Awaitable, Callable
from typing import Any

import aio_pika
from aio_pika.abc import AbstractExchange
from aiormq.exceptions import AMQPError

from app.application.ports.event_publisher import EventPublisherPort
from app.infrastructure.config import get_settings

logger = logging.getLogger(__name__)

_CONNECT_RETRIES = 10
_CONNECT_DELAY_S = 1.0
_PUBLISH_RETRIES = 3
_PUBLISH_BACKOFF_S = 0.05


class RabbitMQPublisher(EventPublisherPort):
    def __init__(self, exchange: AbstractExchange) -> None:
        self._exchange = exchange
        self._lock = asyncio.Lock()

    async def publish(self, event_name: str, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, default=str).encode("utf-8")
        message = aio_pika.Message(
            body=body,
            content_type="application/json",
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        )
        async with self._lock:
            for attempt in range(1, _PUBLISH_RETRIES + 1):
                try:
                    await self._exchange.publish(message, routing_key=event_name)
                    return
                except AMQPError as e:
                    logger.warning(
                        "Falha ao publicar no RabbitMQ (tentativa %s/%s): %s",
                        attempt,
                        _PUBLISH_RETRIES,
                        e,
                    )
                    if attempt == _PUBLISH_RETRIES:
                        raise
                    await asyncio.sleep(_PUBLISH_BACKOFF_S * attempt)


async def create_rabbitmq_publisher() -> (
    tuple[RabbitMQPublisher, Callable[[], Awaitable[None]]]
):
    """
    Cria o publisher, mantém a conexão em memória e devolve um cleanup
    assíncrono para o lifespan do FastAPI.
    """
    url = get_settings().rabbitmq_url
    connection: aio_pika.abc.AbstractRobustConnection
    for attempt in range(1, _CONNECT_RETRIES + 1):
        try:
            connection = await aio_pika.connect_robust(url)
            break
        except Exception as e:
            logger.warning(
                "Falha ao conectar no RabbitMQ (tentativa %s/%s): %s",
                attempt,
                _CONNECT_RETRIES,
                e,
            )
            if attempt == _CONNECT_RETRIES:
                raise
            await asyncio.sleep(_CONNECT_DELAY_S)
    channel = await connection.channel()
    exchange = await channel.declare_exchange(
        "ordering",
        aio_pika.ExchangeType.TOPIC,
        durable=True,
    )
    publisher = RabbitMQPublisher(exchange)

    async def cleanup() -> None:
        await connection.close()

    return publisher, cleanup
