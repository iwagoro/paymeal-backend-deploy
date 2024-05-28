from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, event
from sqlalchemy.sql import func
from database import Base, SessionLocal as Session
from sqlalchemy.dialects.postgresql import ARRAY
from datetime import datetime


class Users(Base):
    __tablename__ = "users"
    id = Column(String(2555), primary_key=True)
    img_url = Column(String(255), nullable=True)
    email = Column(String(255), unique=True)
    notification_token = Column(String(2555), nullable=True)


class AdminUsers(Base):
    __tablename__ = "admin_users"
    id = Column(String(2555), primary_key=True)
    img_url = Column(String(255), nullable=True)
    email = Column(String(255), unique=True)
    notification_token = Column(String(2555), nullable=True)


class Tickets(Base):
    __tablename__ = "tickets"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True)
    description = Column(String(255))
    contents = Column(ARRAY(String), nullable=True)
    img_url = Column(String(255))
    price = Column(Integer)
    stock = Column(Integer)


class Tags(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True)


class TicketTags(Base):
    __tablename__ = "ticket_tags"
    ticket_id = Column(Integer, ForeignKey("tickets.id", ondelete="CASCADE"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)


class Orders(Base):
    __tablename__ = "orders"
    id = Column(String(255), primary_key=True)
    number = Column(Integer, nullable=True)
    user_id = Column(String(2555), ForeignKey("users.id", ondelete="CASCADE"))
    code_id = Column(String(255), nullable=True)
    payment_link = Column(String(255), nullable=True)
    status = Column(String(255))
    total = Column(Integer, nullable=True)
    date = Column(DateTime, nullable=True)


class OrderItems(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True)
    quantity = Column(Integer)
    order_id = Column(String(255), ForeignKey("orders.id", ondelete="CASCADE"))
    ticket_id = Column(Integer, ForeignKey("tickets.id"))
