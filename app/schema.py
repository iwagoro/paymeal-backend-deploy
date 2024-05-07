from pydantic import BaseModel
from datetime import datetime


class Ticket(BaseModel):
    name: str
    description: str
    img_url: str
    price: int
    stock: int

    class Config:
        orm_mode = True


class UserEmail(BaseModel):
    email: str

    class Config:
        orm_mode = True
        
class UserId(BaseModel):
    id: str

    class Config:
        orm_mode = True

class Cart(BaseModel):
    user_id: str
    ticket_id: int

    class Config:
        orm_mode = True


class Order(BaseModel):
    user_id: str
    payment_link: str #支払いリンク
    code_id: str #QRコードのID
    status: str
    date: datetime

    class Config:
        orm_mode = True


class OrderItem(BaseModel):
    order_id: int
    ticket_id: int
    quantity: int

    class Config:
        orm_mode = True

class OrderInfo(BaseModel):
    user_id : str
    order_id : str

    class Config:
        orm_mode = True