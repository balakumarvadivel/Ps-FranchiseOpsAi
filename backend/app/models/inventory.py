from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Numeric, Date, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    contact_person = Column(String(100))
    phone = Column(String(20))
    email = Column(String(150))
    address = Column(Text)
    rating = Column(Numeric(2, 1), default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    products = relationship("Product", back_populates="supplier")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    sku = Column(String(50), unique=True, nullable=False)
    name = Column(String(150), nullable=False)
    category = Column(String(100), nullable=False)
    unit_price = Column(Numeric(12, 2), nullable=False)
    cost_price = Column(Numeric(12, 2), nullable=False)
    reorder_level = Column(Integer, default=20)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    supplier = relationship("Supplier", back_populates="products")
    inventory_rows = relationship("Inventory", back_populates="product")


class Inventory(Base):
    __tablename__ = "inventory"
    __table_args__ = (UniqueConstraint("outlet_id", "product_id"),)

    id = Column(Integer, primary_key=True)
    outlet_id = Column(Integer, ForeignKey("outlets.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Integer, nullable=False, default=0)
    warehouse_status = Column(String(20), default="in_stock")  # in_stock|low_stock|out_of_stock|overstock
    last_restocked = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    outlet = relationship("Outlet", back_populates="inventory")
    product = relationship("Product", back_populates="inventory_rows")
    batches = relationship("InventoryBatch", back_populates="inventory", cascade="all, delete-orphan")


class InventoryBatch(Base):
    __tablename__ = "inventory_batches"

    id = Column(Integer, primary_key=True)
    inventory_id = Column(Integer, ForeignKey("inventory.id", ondelete="CASCADE"), nullable=False)
    batch_number = Column(String(50), nullable=False)
    quantity = Column(Integer, nullable=False)
    manufactured_on = Column(Date)
    expiry_date = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    inventory = relationship("Inventory", back_populates="batches")
