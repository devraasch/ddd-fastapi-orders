from typing import Any

from app.application.ports.event_publisher import EventPublisherPort


class FakeEventPublisher(EventPublisherPort):
    def __init__(self) -> None:
        self.published: list[tuple[str, dict[str, Any]]] = []

    async def publish(self, event_name: str, payload: dict[str, Any]) -> None:
        self.published.append((event_name, payload))
