"""
FastAPI приложение для AiTi Guru
Сервис управления номенклатурой и заказами
"""
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from crud import add_product_to_order
from database import init_db, get_session
from models import Order

from contextlib import asynccontextmanager
import uvicorn


# Lifespan handler вместо on_event
@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="AiTi Guru", lifespan=lifespan)


@app.post("/orders/{order_id}/add-product")
async def add_product(
    order_id: int,
    product_id: int,
    quantity: int,
    session: AsyncSession = Depends(get_session),
):
    try:
        order: Order = await add_product_to_order(session, order_id, product_id, quantity)
        return {
            "order_id": order.id,
            "total_amount": str(order.total_amount),
            "items": [
                {
                    "product_id": item.product_id,
                    "quantity": item.quantity,
                    "price": str(item.price),
                }
                for item in order.items
            ],
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# Точка входа: запускает FastAPI через Uvicorn (python main.py)
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="info", reload=True)
