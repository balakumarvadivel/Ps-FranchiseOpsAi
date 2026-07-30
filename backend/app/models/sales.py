from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Numeric, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True)
    full_name = Column(String(150))
    phone = Column(String(20))
    email = Column(String(150))
    outlet_id = Column(Integer, ForeignKey("outlets.id"))
    first_visit = Column(Date)
    last_visit = Column(Date)
    total_spent = Column(Numeric(14, 2), default=0)
    visit_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    sales = relationship("Sale", back_populates="customer")


class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True)
    outlet_id = Column(Integer, ForeignKey("outlets.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(12, 2), nullable=False)
    total_amount = Column(Numeric(14, 2), nullable=False)
    discount = Column(Numeric(12, 2), default=0)
    sale_date = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    outlet = relationship("Outlet", back_populates="sales")
    product = relationship("Product")
    customer = relationship("Customer", back_populates="sales")
