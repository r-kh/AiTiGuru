"""
CRUD-операции для работы с заказами и товарами.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from decimal import Decimal, ROUND_HALF_UP

from models import Order, OrderItem, Product


# Получить заказ по id
async def get_order(session: AsyncSession, order_id: int) -> Order | None:
    result = await session.execute(select(Order).where(Order.id == order_id))
    return result.scalar_one_or_none()


# Получить товар по id
async def get_product(session: AsyncSession, product_id: int) -> Product | None:
    result = await session.execute(select(Product).where(Product.id == product_id))
    return result.scalar_one_or_none()


# Получить позицию заказа (OrderItem)
async def get_order_item(session: AsyncSession, order_id: int, product_id: int) -> OrderItem | None:
    result = await session.execute(
        select(OrderItem).where(
            OrderItem.order_id == order_id,
            OrderItem.product_id == product_id,
        )
    )
    return result.scalar_one_or_none()


# Обновить общую сумму заказа
async def update_order_total(session: AsyncSession, order: Order) -> None:
    total = sum(
        (item.price * item.quantity for item in order.items),
        Decimal("0.00")
    )
    # округляем до 2 знаков
    order.total_amount = total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    session.add(order)


# Добавление товара в заказ
async def add_product_to_order(
    session: AsyncSession, order_id: int, product_id: int, quantity: int
) -> Order:
    # Проверяем заказ
    order = await get_order(session, order_id)
    if not order:
        raise ValueError("Заказ не найден")

    # Проверяем товар
    product = await get_product(session, product_id)
    if not product:
        raise ValueError("Товар не найден")

    # Проверяем наличие на складе
    if product.quantity < quantity:
        raise ValueError("Недостаточно товара на складе")

    # Проверяем, есть ли уже этот товар в заказе
    order_item = await get_order_item(session, order_id, product_id)

    if order_item:
        # увеличиваем количество
        order_item.quantity += quantity
        session.add(order_item)
    else:
        # создаём новую позицию
        price = product.price.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=quantity,
            price=price,
        )
        session.add(order_item)
        order.items.append(order_item)

    # уменьшаем количество на складе
    product.quantity -= quantity
    session.add(product)

    # пересчитываем итог заказа
    await update_order_total(session, order)

    await session.commit()
    await session.refresh(order)
    return order
