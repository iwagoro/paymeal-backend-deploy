# データベースモデルやセッションを使うための設定を継続使用
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, event
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.sql import func

from dotenv import load_dotenv
import os

load_dotenv()


POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_SERVER = os.getenv("POSTGRES_SERVER")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_DB = os.getenv("POSTGRES_DB")

SQLALCHEMY_DATABASE_URL = "postgresql://{0}:{1}@{2}:{3}/{4}".format(
    POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_SERVER, POSTGRES_PORT, POSTGRES_DB
)
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionClass = sessionmaker(bind=engine)
Base = declarative_base()


#! ユーザ情報
class Users(Base):
    __tablename__ = "users"
    id = Column(
        String(2555),
        primary_key=True,
    )
    email = Column(String(255), unique=True)
    notification_token = Column(String(2555), nullable=True)


#! チケット情報
class Tickets(Base):
    __tablename__ = "tickets"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True)
    description = Column(String(255))
    img_url = Column(String(255))
    price = Column(Integer)
    stock = Column(Integer)


#! 注文情報
class Orders(Base):
    __tablename__ = "orders"
    id = Column(String(255), primary_key=True)
    user_id = Column(String(2555), ForeignKey("users.id", ondelete="CASCADE"))
    code_id = Column(String(255), nullable=True)
    payment_link = Column(String(255), nullable=True)
    status = Column(String(255))  # * not_purchased ,  purchased , ordered , completed
    date = Column(DateTime, nullable=True)


#! 注文アイテム情報
class OrderItems(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True)
    quantity = Column(Integer)
    order_id = Column(String(255), ForeignKey("orders.id", ondelete="CASCADE"))
    ticket_id = Column(Integer, ForeignKey("tickets.id"))


#! 購入された時に日付を更新
def update_order_date(mapper, connection, target):
    if target.status == "purchased" and not target.date:
        target.date = func.now()

    if target.status == "not_purchased" and target.date:
        target.date = None


event.listen(Orders, "before_update", update_order_date)


Base.metadata.create_all(engine)
