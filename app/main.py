from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

from mangum import Mangum
from .endpoints.ticket import router as ticket_router
from .endpoints.user import router as user_router
from .endpoints.cart import router as cart_router
from .endpoints.payment import router as payment_router
from .endpoints.order import router as order_router
from .endpoints.notification import router as notification_router
from firebase_admin import credentials
import firebase_admin

# FastAPI のアプリケーションを作成
app = FastAPI()

cred = credentials.Certificate("firebase-admin.json")  # Firebase Admin SDK キー
firebase_admin.initialize_app(cred)

origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:3000",
    "http://localhost:3001",
    "https://localhost:3000",
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
app.include_router(order_router)
app.include_router(notification_router)
