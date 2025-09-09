"""
models.py — описание структуры БД через ORM SQLModel.
Здесь определяются таблицы (Category, Product, Customer, Order, OrderItem)
и их связи (ForeignKey, Relationship).
"""

from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Numeric
from datetime import datetime
from decimal import Decimal


# ----------------------
# Категории товаров
# ----------------------
class Category(SQLModel, table=True):
    __tablename__ = "categories"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=255)
    parent_id: Optional[int] = Field(default=None, foreign_key="categories.id")
    top_level_id: int

    children: list["Category"] = Relationship(
        back_populates="parent",
        sa_relationship_kwargs={"remote_side": "Category.id"}
    )
    parent: Optional["Category"] = Relationship(back_populates="children")

# ----------------------
# Номенклатура
# ----------------------
class Product(SQLModel, table=True):
    __tablename__ = "products"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=255)
    quantity: int
    price: Decimal = Field(sa_column=Numeric(11, 2))
    category_id: int = Field(foreign_key="categories.id")

    category: Optional[Category] = Relationship()

# ----------------------
# Клиенты
# ----------------------
class Client(SQLModel, table=True):
    __tablename__ = "clients"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=255)
    address: Optional[str] = Field(default=None, max_length=255)

# ----------------------
# Заказы
# ----------------------
class Order(SQLModel, table=True):
    __tablename__ = "orders"

    id: Optional[int] = Field(default=None, primary_key=True)
    client_id: int = Field(foreign_key="clients.id")
    order_date: datetime = Field(default_factory=datetime.utcnow)
    status: str = Field(max_length=50)
    total_amount: Decimal = Field(default=0, sa_column=Numeric(11, 2))

    client: Optional[Client] = Relationship()
    items: list["OrderItem"] = Relationship(
        back_populates="order",
        sa_relationship_kwargs={"lazy": "selectin"}
    )


# ----------------------
# Позиции заказа
# ----------------------
class OrderItem(SQLModel, table=True):
    __tablename__ = "order_items"

    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="orders.id")
    product_id: int = Field(foreign_key="products.id")
    quantity: int
    price: Decimal = Field(sa_column=Numeric(11, 2))

    order: Optional[Order] = Relationship(back_populates="items")
    product: Optional[Product] = Relationship()
