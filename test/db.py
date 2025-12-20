import os
import mysql.connector
from datetime import datetime
from decimal import Decimal


def _cfg():
    return dict(
        host=os.getenv("MYSQL_HOST", "mysql"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", "root"),
        database=os.getenv("MYSQL_DATABASE", "orders_db"),
    )


def init_db():
    cfg = _cfg()
    conn = mysql.connector.connect(
        host=cfg["host"],
        port=cfg["port"],
        user=cfg["user"],
        password=cfg["password"],
        autocommit=True,
    )
    cur = conn.cursor()
    cur.execute(f"CREATE DATABASE IF NOT EXISTS {cfg['database']}")
    cur.execute(f"USE {cfg['database']}")

    cur.execute("SHOW TABLES LIKE 'orders'")
    if cur.fetchone() is None:
        raise RuntimeError("Table 'orders' does not exist in orders_db.")

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS order_items (
            order_id VARCHAR(20) NOT NULL,
            item_id VARCHAR(20) NOT NULL,
            quantity INT NOT NULL,
            price DECIMAL(10,2) NOT NULL,
            created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (order_id, item_id)
        ) ENGINE=InnoDB;
        """
    )

    cur.close()
    conn.close()


def _require(order: dict, key: str):
    val = order.get(key)
    if val is None or val == "":
        raise ValueError(f"Missing required field: {key}")
    return val


def _normalize_order_date(value):
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace("Z", "").replace("T", " "))
        except ValueError:
            pass
    return datetime.now()


def _serialize_dt(v):
    if isinstance(v, datetime):
        return v.isoformat(sep=" ")
    if isinstance(v, Decimal):
        return float(v)
    return v


def save_order(order: dict):
    order_id = _require(order, "orderId")
    customer_id = _require(order, "customerId")
    currency = _require(order, "currency")
    status = _require(order, "status")
    total_amount = _require(order, "totalAmount")
    order_date = _normalize_order_date(order.get("orderDate"))

    items = order.get("items") or []
    if not isinstance(items, list):
        raise ValueError("items must be a list")

    cfg = _cfg()
    conn = mysql.connector.connect(
        host=cfg["host"],
        port=cfg["port"],
        user=cfg["user"],
        password=cfg["password"],
        database=cfg["database"],
    )

    try:
        conn.start_transaction()
        cur = conn.cursor()

        cur.execute(
            """
            INSERT IGNORE INTO orders
            (order_id, customer_id, currency, status, total_amount, order_date)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                str(order_id),
                str(customer_id),
                str(currency),
                str(status),
                total_amount,
                order_date,
            ),
        )

        inserted_order = (cur.rowcount == 1)

        if not inserted_order:
            conn.commit()
            cur.close()
            return False

        for it in items:
            item_id = it.get("itemId")
            quantity = it.get("quantity")
            price = it.get("price")

            if not item_id or quantity is None or price is None:
                continue

            cur.execute(
                """
                INSERT IGNORE INTO order_items
                (order_id, item_id, quantity, price)
                VALUES (%s, %s, %s, %s)
                """,
                (str(order_id), str(item_id), int(quantity), price),
            )

        conn.commit()
        cur.close()
        return True

    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_order(order_id: str):
    cfg = _cfg()
    conn = mysql.connector.connect(
        host=cfg["host"],
        port=cfg["port"],
        user=cfg["user"],
        password=cfg["password"],
        database=cfg["database"],
    )

    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(
            """
            SELECT order_id, customer_id, currency, status, total_amount, order_date
            FROM orders
            WHERE order_id = %s
            """,
            (str(order_id),),
        )
        order_row = cur.fetchone()
        if not order_row:
            cur.close()
            return None

        cur.execute(
            """
            SELECT order_id, item_id, quantity, price, created_at
            FROM order_items
            WHERE order_id = %s
            ORDER BY item_id
            """,
            (str(order_id),),
        )
        items_rows = cur.fetchall()
        cur.close()

        order_row = {k: _serialize_dt(v) for k, v in order_row.items()}
        items_rows = [{k: _serialize_dt(v) for k, v in r.items()} for r in items_rows]
        order_row["items"] = items_rows
        return order_row

    finally:
        conn.close()
