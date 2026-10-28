import sqlite3
from contextlib import closing
from pathlib import Path


class ProductList:
    def __init__(self) -> None:
        self.database_path = Path(__file__).with_name("MyProduct.db")
        with closing(sqlite3.connect(self.database_path)) as connection:
            with connection:
                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS Products (
                        productID INTEGER PRIMARY KEY,
                        productName TEXT NOT NULL,
                        productPrice INTEGER NOT NULL
                    )
                    """
                )

    def insert_product(
        self, product_id: int, product_name: str, product_price: int
    ) -> None:
        with closing(sqlite3.connect(self.database_path)) as connection:
            with connection:
                connection.execute(
                    """
                    INSERT INTO Products (productID, productName, productPrice)
                    VALUES (?, ?, ?)
                    """,
                    (product_id, product_name, product_price),
                )

    def update_product(
        self, product_id: int, product_name: str, product_price: int
    ) -> bool:
        with closing(sqlite3.connect(self.database_path)) as connection:
            with connection:
                cursor = connection.execute(
                    """
                    UPDATE Products
                    SET productName = ?, productPrice = ?
                    WHERE productID = ?
                    """,
                    (product_name, product_price, product_id),
                )
                return cursor.rowcount > 0

    def delete_product(self, product_id: int) -> bool:
        with closing(sqlite3.connect(self.database_path)) as connection:
            with connection:
                cursor = connection.execute(
                    "DELETE FROM Products WHERE productID = ?",
                    (product_id,),
                )
                return cursor.rowcount > 0

    def select_products(
        self, product_id: int | None = None
    ) -> list[tuple[int, str, int]]:
        with closing(sqlite3.connect(self.database_path)) as connection:
            if product_id is None:
                rows = connection.execute(
                    """
                    SELECT productID, productName, productPrice
                    FROM Products
                    ORDER BY productID
                    """
                ).fetchall()
            else:
                rows = connection.execute(
                    """
                    SELECT productID, productName, productPrice
                    FROM Products
                    WHERE productID = ?
                    """,
                    (product_id,),
                ).fetchall()
            return rows

    def seed_sample_data(self) -> None:
        sample_products = [
            (
                product_id,
                f"전자제품 {product_id:04d}",
                10000 + (product_id - 1) * 1000,
            )
            for product_id in range(1, 1001)
        ]
        with closing(sqlite3.connect(self.database_path)) as connection:
            with connection:
                connection.executemany(
                    """
                    INSERT OR IGNORE INTO Products
                        (productID, productName, productPrice)
                    VALUES (?, ?, ?)
                    """,
                    sample_products,
                )


if __name__ == "__main__":
    products = ProductList()
    products.seed_sample_data()
    print(f"등록된 제품 수: {len(products.select_products())}")
