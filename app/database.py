# データベースモデルやセッションを使うための設定を継続使用
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, event
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.sql import func
import uuid

engine = create_engine("sqlite:///sample_db.sqlite3", echo=True)
SessionClass = sessionmaker(bind=engine)
Base = declarative_base()


class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True)


class Tickets(Base):
    __tablename__ = "tickets"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True)
    description = Column(String(255))
    img_url = Column(String(255))
    price = Column(Integer)
    stock = Column(Integer)


class Orders(Base):
    __tablename__ = "orders"
    id = Column(String(255), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    code_id = Column(String(255),nullable=True)
    payment_link = Column(String(255),nullable=True)
    status = Column(String(255))  # not_purchased , processing  ,  purchased , ordered , completed
    date = Column(DateTime, nullable=True)


class OrderItems(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True)
    quantity = Column(Integer)
    order_id = Column(String(255), ForeignKey("orders.id"))
    ticket_id = Column(Integer, ForeignKey("tickets.id"))


def update_order_date(mapper, connection, target):
    if target.status == "purchased" and not target.date:
        target.date = func.now()

    if target.status == "not_purchased" and target.date:
        target.date = None


event.listen(Orders, "before_update", update_order_date)


Base.metadata.create_all(engine)


##TZ が違う
