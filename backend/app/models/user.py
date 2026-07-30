from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text, Numeric, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)

    users = relationship("User", back_populates="role")


class Outlet(Base):
    __tablename__ = "outlets"

    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    code = Column(String(20), unique=True, nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    region = Column(String(50), nullable=False)
    address = Column(Text)
    latitude = Column(Numeric(9, 6))
    longitude = Column(Numeric(9, 6))
    opened_on = Column(Date)
    status = Column(String(20), default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    users = relationship("User", back_populates="outlet")
    sales = relationship("Sale", back_populates="outlet")
    inventory = relationship("Inventory", back_populates="outlet")
    employees = relationship("Employee", back_populates="outlet")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    full_name = Column(String(150), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    outlet_id = Column(Integer, ForeignKey("outlets.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    reset_token = Column(String(255), nullable=True)
    reset_token_expires = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    role = relationship("Role", back_populates="users")
    outlet = relationship("Outlet", back_populates="users")
