from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from firebase_admin import credentials
import firebase_admin
from database import engine, init_db
from typing import Any, Optional
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from endpoints.tickets import router as ticket_router
from endpoints.user import router as user_router
from endpoints.cart import router as cart_router
from endpoints.payment import router as payment_router
from endpoints.order import router as order_router
from fastapi import FastAPI
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

# Initialize the database
init_db()

# Initialize Firebase
cred = credentials.Certificate("firebase-admin.json")
firebase_admin.initialize_app(cred)


app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:3001",
    "https://paymeal-admin.vercel.app",
    "https://pay-meal.vercel.app",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(ticket_router)
app.include_router(user_router)
app.include_router(cart_router)
app.include_router(payment_router)
app.include_router(order_router)
