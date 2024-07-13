from uuid import UUID

import pytest
from httpx import AsyncClient
from application.cmd import app
from application.schemas import UpdateBookS, UpdatePartiallyBookS


@pytest.mark.asyncio
@pytest.fixture(scope="session")
async def get_admin_header() -> str:
    data = {"email": "jordan@gmail.com", "password": "123456"}
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(url="auth/login", json=data)
        admin_header = f"Bearer {response.json()['token']}"
        return admin_header


@pytest.mark.asyncio(scope="session")
@pytest.mark.parametrize(
    "book_id,status_code",
    [
        ("657dab80-50ff-45d9-a242-ac0357d97417", 200),
        ("0b003aac-25dc-4fd6-8f89-e2ba796c6385", 404),
    ],
)
async def test_get_book_by_id(
        book_id: int | str, status_code: int, get_admin_header: str
):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(
            url=f"books/{book_id}", headers={"Authorization": get_admin_header}
        )
    assert response.status_code == status_code


@pytest.mark.asyncio(scope="session")
async def test_get_all_books():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(url="books/")
    assert response.status_code == 200


@pytest.mark.asyncio(scope="session")
@pytest.mark.parametrize(
    "isbn,name,description,price_per_unit,number_in_stock,genre_name,rating,discount,status_code",
    [
        ("5555", "New Book", "", 10, 100, "fantasy", 5, 10, 201),
        ("5555", "New Book", "", 10, 100, "fantasy", 5, 10, 409),
        ("3333", "New Book 3", "description", 0, 100, "fantasy", 5, 10, 422),
        ("3333", "New Book 3", "description", 2, -1, "fantasy", 5, 10, 422),
        ("3333", "", "description", 10, 1, "fantasy", 5, 10, 422),
        ("", "New Book 4", "description", 10, 1, "fantasy", 5, 10, 422),
        ("7777", "New Book 4", "description", 10, 1, "", 5, 10, 422),
    ],
)
async def test_create_book(
        isbn: str,
        name: str,
        description: str,
        price_per_unit: int,
        number_in_stock: int,
        genre_name: str,
        rating: float,
        discount: int,
        status_code: int,
):
    data = {
        "isbn": isbn,
        "name": name,
        "description": description,
        "price_per_unit": price_per_unit,
        "number_in_stock": number_in_stock,
        "genre_name": genre_name,
        "rating": rating,
        "discount": discount,
    }
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(url="books/", json=data)
    assert response.status_code == status_code


@pytest.mark.asyncio(scope="session")
@pytest.mark.parametrize(
    "book_id,status_code",
    [
        ("657dab80-50ff-45d9-a242-ac0357d97417", 204),
        ("657dab80-50ff-45d9-a242-ac0357d97417", 404),
    ],
)
async def test_delete_book(book_id, status_code):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.delete(url=f"books/{book_id}")
    assert response.status_code == status_code


@pytest.mark.asyncio(scope="session")
@pytest.mark.parametrize(
    "book_id,update_data,status_code",
    [
        (
                "ecd38a11-3bbd-4bba-b596-3e2d554796a7",
                {
                    "name": "Book for update122221",
                    "description": "book for update",
                    "price_per_unit": 66.5,
                    "number_in_stock": 5,
                    "isbn": "1010101",
                    "genre_name": "Horror",
                    "rating": 2.8,
                    "discount": 10
                },
                200,
        ),
        (
                "ecd38a11-3bbd-4bba-b596-3e2d554796a7",
                {
                    "isbn": "1010101",
                    "name": "Book updated",
                    "price_per_unit": 85.4,
                    "number_in_stock": 84,
                    "genre_name": "Genre Updated",
                    "rating": 3,
                    "discount": -10
                },
                422,
        ),
        (
                "ebd38a11-3bbd-4bba-b596-3e2d554796a7",
                {
                    "name": "Book for update122221",
                    "description": "book for update",
                    "price_per_unit": 66.5,
                    "number_in_stock": 5,
                    "isbn": "1010101",
                    "genre_name": "Horror",
                    "rating": 6,
                    "discount": 10
                },
                404,
        ),
    ],
)
async def test_update_book(book_id: int | str, update_data: UpdateBookS, status_code):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.put(url=f"books/{book_id}", json=update_data)
    assert response.status_code == status_code


@pytest.mark.asyncio(scope="session")
@pytest.mark.parametrize(
    "book_id,update_data,status_code",
    [
        (
                "ecd38a11-3bbd-4bba-b596-3e2d554796a7",
                {
                    "name": "string",
                    "description": "string",
                    "price_per_unit": 5,
                    "number_in_stock": 10,
                    "genre_name": "string",
                    "rating": 5,
                    "discount": 5
                },
                200
        ),
        (
                "ecd38a11-3bbd-4bba-b596-3e2d554796a7",
                {
                    "name": "string",
                    "description": "string",
                    "price_per_unit": 5,
                    "number_in_stock": 0,
                    "genre_name": "string",
                    "rating": 0,
                    "discount": 0
                },
                422
        ),
    ]
)
async def test_update_book_partially(
        book_id: str,
        update_data: dict,
        status_code: int
):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.patch(url=f"books/{book_id}", json=update_data)
    assert response.status_code == status_code
