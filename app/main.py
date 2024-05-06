from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .schema import Ticket, User, Order, OrderItem
from .database import Tickets, Users, SessionClass, Orders, OrderItems
from fastapi.middleware.cors import CORSMiddleware
from .paypay import create_payment

from mangum import Mangum
from .endpoints.ticket import router as ticket_router
from .endpoints.user import router as user_router
from .endpoints.cart import router as cart_router
from .endpoints.payment import router as payment_router

# FastAPI のアプリケーションを作成
app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:3000",
    "http://localhost:3001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


handler = Mangum(app)
app.include_router(ticket_router)
app.include_router(user_router)
app.include_router(cart_router)
app.include_router(payment_router)