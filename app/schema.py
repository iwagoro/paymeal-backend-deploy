from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Any
from fastapi import HTTPException


#! 管理者登録の情報を格納するためのクラス
class AdminSchema(BaseModel):
    password: str

    class Config:
        orm_mode = True


#! チケットの情報を格納するためのクラス
class TicketSchema(BaseModel):
    name: str
    description: str
    img_url: str
    price: int
    stock: int
    contents: list = []

    class Config:
        orm_mode = True


#!　タグの情報を格納するためのクラス
class TagSchema(BaseModel):
    name: str

    class Config:
        orm_mode = True


#! チケットとタグの関連情報を格納するためのクラス
class TicketTagSchema(BaseModel):
    tags: list = []

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


class ResponseModel(BaseModel):
    code: int
    message: str
    data: Optional[Any] = None


class ErrorResponseModel(BaseModel):
    code: int
    message: str
