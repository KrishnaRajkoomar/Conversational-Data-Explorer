from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()


class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    region = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    orders = relationship("Order", back_populates="customer")


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    product = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(String, nullable=False)
    order_date = Column(DateTime, default=datetime.utcnow)
    customer = relationship("Customer", back_populates="orders")
    payments = relationship("Payment", back_populates="order")


class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    amount = Column(Float, nullable=False)
    paid_at = Column(DateTime, nullable=True)
    method = Column(String, nullable=False)
    order = relationship("Order", back_populates="payments")
