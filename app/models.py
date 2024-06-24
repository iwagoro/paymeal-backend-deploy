from sqlalchemy import Column, Integer, String, ForeignKey, Date,JSON
from sqlalchemy.orm import relationship
from database import Base
from sqlalchemy.dialects.postgresql import ARRAY


#! ユーザーテーブル
class Users(Base):
    __tablename__ = "users"
    id = Column(String(255), primary_key=True)
    email = Column(String(255), unique=True)
    notification_token = Column(String(255), nullable=True)


#! 管理者テーブル
class AdminUsers(Base):
    __tablename__ = "admin_users"
    id = Column(String(255), primary_key=True)
    email = Column(String(255), unique=True)
    username = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    

#! 日替わりメニューテーブル
class DailyMenus(Base):
    __tablename__ = "daily_menus"
    ticket_id = Column(Integer, ForeignKey("tickets.id", ondelete="CASCADE"), primary_key=True)
    contents = Column(JSON, nullable=False)
    date = Column(Date, nullable=False, primary_key=True)

    ticket = relationship("Tickets", back_populates="daily_menus")

#! 食券テーブル
class Tickets(Base):
    __tablename__ = "tickets"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True)
    description = Column(String(255))
    contents = Column(ARRAY(String), nullable=True)
    img_url = Column(String(255))
    price = Column(Integer)

    stocks = relationship("Stocks", back_populates="ticket", uselist=False)
    tags = relationship("TagRelations", back_populates="ticket")
    popular_menus = relationship("PopularMenus", back_populates="ticket", uselist=False)
    daily_menus = relationship("DailyMenus", back_populates="ticket", uselist=False)    

#! 在庫テーブル
class Stocks(Base):
    __tablename__ = "stocks"
    ticket_id = Column(Integer, ForeignKey("tickets.id", ondelete="CASCADE"), primary_key=True)
    stock = Column(Integer)
    unit_sales = Column(Integer, default=0)

    ticket = relationship("Tickets", back_populates="stocks")


#! 人気メニューテーブル
class PopularMenus(Base):
    __tablename__ = "popular_menus"
    ticket_id = Column(Integer, ForeignKey("tickets.id", ondelete="CASCADE"), primary_key=True)
    ranking = Column(Integer, nullable=False)  # 人気の順位を保持
    date = Column(Date, nullable=False,primary_key=True)  # 計算した日付を保持

    ticket = relationship("Tickets", back_populates="popular_menus")

#! 食券のタグテーブル
class Tags(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True)

    tickets = relationship("TagRelations", back_populates="tag")

#! 食券とタグの関連テーブル
class TagRelations(Base):
    __tablename__ = "tag_relations"
    ticket_id = Column(Integer, ForeignKey("tickets.id", ondelete="CASCADE"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)
    
    ticket = relationship("Tickets", back_populates="tags")
    tag = relationship("Tags", back_populates="tickets")

#! 注文テーブル
class Orders(Base):
    __tablename__ = "orders"
    id = Column(String(255), primary_key=True)
    number = Column(Integer, nullable=True)
    user_id = Column(String(255), ForeignKey("users.id", ondelete="CASCADE"))
    code_id = Column(String(255), nullable=True)
    payment_link = Column(String(255), nullable=True)
    status = Column(String(255))
    total = Column(Integer)
    purchase_date = Column(Date, nullable=True)
    order_date = Column(Date, nullable=True)

    user = relationship("Users", back_populates="orders")
    items = relationship("OrderItems", back_populates="order")

Users.orders = relationship("Orders", order_by=Orders.id, back_populates="user")

#! 注文内容テーブル
class OrderItems(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True)
    quantity = Column(Integer)
    order_id = Column(String(255), ForeignKey("orders.id", ondelete="CASCADE"))
    ticket_id = Column(Integer, ForeignKey("tickets.id"))

    order = relationship("Orders", back_populates="items")
    ticket = relationship("Tickets")

# ここにテストコードやその他のコードを記述します
