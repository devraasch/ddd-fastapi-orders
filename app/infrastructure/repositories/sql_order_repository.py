from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.order import Order
from app.domain.entities.order_item import OrderItem
from app.domain.repositories.order_repository import OrderRepository
from app.domain.value_objects.order_status import OrderStatus
from app.infrastructure.database.models import OrderModel


class SqlOrderRepository(OrderRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, order: Order) -> Order:
        row = OrderModel(
            customer_name=order.customer_name,
            total=order.total,
            status=order.status.value,
        )
        self._session.add(row)
        await self._session.commit()
        await self._session.refresh(row)
        return Order(
            id=row.id,
            customer_name=row.customer_name,
            status=OrderStatus(row.status),
            items=[
                OrderItem(
                    product_id=i.product_id,
                    quantity=i.quantity,
                    unit_price=i.unit_price,
                )
                for i in order.items
            ],
        )
