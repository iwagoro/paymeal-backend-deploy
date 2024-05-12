from pydantic import BaseModel
from datetime import datetime


#! チケットの情報を格納するためのクラス
class TicketSchema(BaseModel):
    name: str
    description: str
    img_url: str
    price: int
    stock: int

    class Config:
        orm_mode = True


#! カートの情報を格納するためのクラス
class CartSchema(BaseModel):
    user_id: str
    ticket_id: int

    class Config:
        orm_mode = True


#! 注文の情報を格納するためのクラス
class OrderSchema(BaseModel):
    user_id: str
    payment_link: str  # 支払いリンク
    code_id: str  # QRコードのID
    status: str
    date: datetime

    class Config:
        orm_mode = True


#! 注文アイテムの情報を格納するためのクラス
class submitNotificationSchema(BaseModel):
    token: str

    class Config:
        orm_mode = True


#! 通知の情報を格納するためのクラス
class sendNotificationSchema(BaseModel):
    target_id: str
    title: str
    body: str

    class Config:
        orm_mode = True
