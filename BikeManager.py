import sqlite3
from contextlib import closing
from pathlib import Path


class BikeManager:
    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path
        with closing(sqlite3.connect(self.database_path)) as connection:
            with connection:
                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS MyProduct (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        price INTEGER NOT NULL
                    )
                    """
                )

    def add_product(self, name: str, price: int) -> None:
        with closing(sqlite3.connect(self.database_path)) as connection:
            with connection:
                connection.execute(
                    "INSERT INTO MyProduct (name, price) VALUES (?, ?)",
                    (name, price),
                )

    def update_product(self, product_id: int, name: str, price: int) -> bool:
        with closing(sqlite3.connect(self.database_path)) as connection:
            with connection:
                cursor = connection.execute(
                    """
                    UPDATE MyProduct
                    SET name = ?, price = ?
                    WHERE id = ?
                    """,
                    (name, price, product_id),
                )
                return cursor.rowcount > 0

    def delete_product(self, product_id: int) -> bool:
        with closing(sqlite3.connect(self.database_path)) as connection:
            with connection:
                cursor = connection.execute(
                    "DELETE FROM MyProduct WHERE id = ?",
                    (product_id,),
                )
                return cursor.rowcount > 0

    def search_products(self, name: str = "") -> list[tuple[int, str, int]]:
        with closing(sqlite3.connect(self.database_path)) as connection:
            if name:
                return connection.execute(
                    """
                    SELECT id, name, price
                    FROM MyProduct
                    WHERE name LIKE ?
                    ORDER BY id
                    """,
                    (f"%{name}%",),
                ).fetchall()
            return connection.execute(
                "SELECT id, name, price FROM MyProduct ORDER BY id"
            ).fetchall()
