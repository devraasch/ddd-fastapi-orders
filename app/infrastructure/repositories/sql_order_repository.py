from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.entities.order import Order
from app.domain.entities.order_item import OrderItem
from app.domain.repositories.order_repository import OrderRepository
from app.domain.value_objects.order_status import OrderStatus
from app.infrastructure.database.models import OrderItemModel, OrderModel


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
        await self._session.flush()
        for item in order.items:
            self._session.add(
                OrderItemModel(
                    order_id=row.id,
                    product_id=item.product_id,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                )
            )
        await self._session.commit()
        loaded = await self._load_order_with_items(row.id)
        return self._to_domain(loaded)

    async def get_by_id(self, order_id: int) -> Order | None:
        row = await self._load_order_with_items_or_none(order_id)
        if row is None:
            return None
        return self._to_domain(row)

    async def list_all(self) -> list[Order]:
        result = await self._session.execute(
            select(OrderModel)
            .options(selectinload(OrderModel.items))
            .order_by(OrderModel.id)
        )
        rows = result.scalars().all()
        return [self._to_domain(row) for row in rows]

    async def update(self, order: Order) -> Order | None:
        if order.id is None:
            raise ValueError("order id is required to update")
        row = await self._session.get(OrderModel, order.id)
        if row is None:
            return None
        row.customer_name = order.customer_name
        row.total = order.total
        row.status = order.status.value
        await self._session.commit()
        loaded = await self._load_order_with_items_or_none(order.id)
        if loaded is None:
            return None
        return self._to_domain(loaded)

    async def _load_order_with_items(self, order_id: int) -> OrderModel:
        result = await self._session.execute(
            select(OrderModel)
            .where(OrderModel.id == order_id)
            .options(selectinload(OrderModel.items))
        )
        return result.scalar_one()

    async def _load_order_with_items_or_none(self, order_id: int) -> OrderModel | None:
        result = await self._session.execute(
            select(OrderModel)
            .where(OrderModel.id == order_id)
            .options(selectinload(OrderModel.items))
        )
        return result.scalar_one_or_none()

    def _to_domain(self, row: OrderModel) -> Order:
        lines = sorted(row.items, key=lambda line: line.id)
        return Order(
            id=row.id,
            customer_name=row.customer_name,
            status=OrderStatus(row.status),
            items=[
                OrderItem(
                    product_id=line.product_id,
                    quantity=line.quantity,
                    unit_price=line.unit_price,
                )
                for line in lines
            ],
        )
