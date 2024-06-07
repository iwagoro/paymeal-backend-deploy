from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from firebase_admin import credentials
import firebase_admin
from database import engine, init_db
from typing import Any, Optional
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from endpoints.ticket.admin import router as ticket_router_admin
from endpoints.ticket.user import router as ticket_router_user
from endpoints.user.user import router as user_router_user
from endpoints.user.admin import router as user_router_admin
from endpoints.cart.user import router as cart_router
from endpoints.payment import router as payment_router
from endpoints.order.user import router as order_router_user
from endpoints.order.admin import router as order_router_admin
from endpoints.analytics import router as analytics_router
from fastapi import FastAPI, Response
import pytz

# Initialize the database
init_db()

# Initialize Firebase
cred = credentials.Certificate("firebase-admin.json")
firebase_admin.initialize_app(cred)

# Create FastAPI app
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
app.include_router(ticket_router_admin)
app.include_router(ticket_router_user)
app.include_router(user_router_user)
app.include_router(user_router_admin)
app.include_router(cart_router)
app.include_router(payment_router)
app.include_router(order_router_user)
app.include_router(order_router_admin)
app.include_router(analytics_router)
