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


class User(BaseModel):
    email: str

    class Config:
        orm_mode = True


class Order(BaseModel):
    user_id: int
    payment_link: str
    code_id: str
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
