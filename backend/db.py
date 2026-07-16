import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine, inspect as sa_inspect
from sqlalchemy.orm import sessionmaker
from .models import Base, Customer, Order, Payment

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data.db")
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)
SessionLocal = sessionmaker(bind=engine)


def init_db():
    Base.metadata.create_all(engine)


def seed_data():
    session = SessionLocal()
    if session.query(Customer).count() > 0:
        session.close()
        return

    regions = ["North", "South", "East", "West"]
    customers = []
    for i in range(20):
        c = Customer(
            name=f"Customer {i+1}",
            email=f"customer{i+1}@example.com",
            region=regions[i % 4],
        )
        session.add(c)
        customers.append(c)
    session.flush()

    products = ["Widget A", "Widget B", "Gadget X", "Gadget Y", "Service Z"]
    statuses = ["pending", "shipped", "delivered", "cancelled"]
    orders = []
    for i in range(50):
        o = Order(
            customer_id=customers[i % 20].id,
            product=products[i % 5],
            amount=round((i + 1) * 25.0 + (i % 7) * 10.0, 2),
            status=statuses[i % 4],
            order_date=datetime.utcnow() - timedelta(days=i * 2),
        )
        session.add(o)
        orders.append(o)
    session.flush()

    methods = ["credit_card", "bank_transfer", "cash"]
    for i in range(30):
        p = Payment(
            order_id=orders[i % 50].id,
            amount=orders[i % 50].amount * 0.9,
            paid_at=datetime.utcnow() - timedelta(days=max(i * 2, 1)),
            method=methods[i % 3],
        )
        session.add(p)

    session.commit()
    session.close()


def get_db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def get_schema_text():
    inspector = sa_inspect(engine)
    lines = []
    for table_name in inspector.get_table_names():
        lines.append(f"Table: {table_name}")
        for col in inspector.get_columns(table_name):
            pk = " PK" if col["primary_key"] else ""
            nullable = "" if col["nullable"] else " NOT NULL"
            lines.append(f"  {col['name']} ({col['type']}){pk}{nullable}")
        for fk in inspector.get_foreign_keys(table_name):
            for col, ref_col in zip(fk["constrained_columns"], fk["referred_columns"]):
                lines.append(
                    f"  {col} → {fk['referred_table']}.{ref_col}"
                )
        lines.append("")
    return "\n".join(lines)
