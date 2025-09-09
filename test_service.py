import asyncio
import subprocess
from database import init_db, async_session
from models import Category, Product, Client, Order
import time


async def seed():
    await init_db()

    async with async_session() as session:
        cat_tv = Category(id=1, name="Телевизоры", parent_id=None, top_level_id=1)
        cat_wm = Category(id=2, name="Стиральные машины", parent_id=None, top_level_id=2)
        session.add_all([cat_tv, cat_wm])
        await session.commit()

        product1 = Product(id=1, name="SONY TV", quantity=10, price=500.00, category_id=1)
        product2 = Product(id=2, name="BOSCH WM", quantity=5, price=799.99, category_id=2)
        session.add_all([product1, product2])
        await session.commit()

        client1 = Client(id=1, name='ООО "Ромашка"', address="г. Москва, ул. Ленина, 10")
        client2 = Client(id=2, name='ИП Петров', address="г. Санкт-Петербург, Невский пр., 5")
        session.add_all([client1, client2])
        await session.commit()

        order1 = Order(id=1, client_id=1, status="NEW")
        order2 = Order(id=2, client_id=2, status="NEW")
        session.add_all([order1, order2])
        await session.commit()

    print("Seed data added!")


def check(cmd, expected_substring):
    result = subprocess.run(cmd, capture_output=True, text=True)
    output = result.stdout.strip()
    print(output)
    if expected_substring in output:
        print("✅ Passed")
    else:
        print("❌ Failed")


def run_curl_tests():
    print("\n--- Running test API calls ---\n")
    time.sleep(1)

    print("1. Добавляем новый товар в заказ")
    check(
        ["curl", "-s", "-X", "POST", "http://localhost:8000/orders/1/add-product?product_id=1&quantity=2"],
        '"total_amount":"1000.00"'
    )

    time.sleep(1)
    print("\n2. Добавляем тот же товар еще раз (количество должно увеличиться, а не создаться новая позиция)")
    check(
        ["curl", "-s", "-X", "POST", "http://localhost:8000/orders/1/add-product?product_id=1&quantity=3"],
        '"quantity":5'   # вместо проверки только суммы явно проверяем увеличение количества
    )

    time.sleep(1)
    print("\n3. Пытаемся добавить товар больше, чем есть на складе (ожидаем ошибку)")
    check(
        ["curl", "-s", "-X", "POST", "http://localhost:8000/orders/1/add-product?product_id=2&quantity=10"],
        '"Недостаточно товара на складе"'
    )

    time.sleep(1)
    print("\n4. Добавляем другой товар (должна появиться новая позиция)")
    check(
        ["curl", "-s", "-X", "POST", "http://localhost:8000/orders/1/add-product?product_id=2&quantity=2"],
        '"product_id":2'
    )



if __name__ == "__main__":
    asyncio.run(seed())
    run_curl_tests()
