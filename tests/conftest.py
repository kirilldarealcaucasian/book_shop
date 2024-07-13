import json
from typing import Generator
import pytest
import pytest_asyncio
import asyncio
from httpx import AsyncClient
from sqlalchemy import insert
from core import settings, db_config
from application.models import Base, User, Book, BookOrderAssoc, Author, Publisher, Order, Image
from application.cmd import app
import os


@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_database():
    assert settings.MODE == "TEST"

    async with db_config.engine.begin() as con:
        await con.run_sync(Base.metadata.drop_all)
        await con.run_sync(Base.metadata.create_all)

    def open_test_data_json(model: str) -> dict:
        with open(os.path.abspath(f"tests/test_data/{model}.json"), "r", encoding="utf-8") as file:
            return json.load(file)

    users: dict = open_test_data_json("users")
    books: dict = open_test_data_json("books")
    orders: dict = open_test_data_json("orders")
    authors: dict = open_test_data_json("authors")
    publishers: dict = open_test_data_json("publishers")
    book_order_assoc: dict = open_test_data_json("book_order_assoc")
    images: dict = open_test_data_json("images")

    db_models = [User, Book, Author, Publisher, Order, BookOrderAssoc, Image]
    db_to_add_data = [users,  books, authors, publishers, orders, book_order_assoc, images]

    async with db_config.async_session() as session:
        for model, data in zip(db_models, db_to_add_data):
            stmt = insert(model).values(data)
            await session.execute(stmt)
            await session.commit()


@pytest.mark.asyncio
@pytest.fixture(scope="function")
async def ac():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="session", autouse=True)
def event_loop() -> Generator:
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


