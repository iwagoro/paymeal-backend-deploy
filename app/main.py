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

ALGORITHM = "HS256"

SECRET_KEY = "PTlFH2aumohWt0ubq5Mfp2Y2vKF548kwHpye1QX6HQU="


@app.get("/test")
async def get_current_user():
    encoded_jwt = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiIsImtpZCI6InE3UDFOdnh1R1F3RE4yVGFpTW92alo4YVp3cyJ9.eyJhdWQiOiJmYWQ1NjI0YS1mOTA0LTRiMjMtODc1OC0wNjJiMGM1MTM2NjEiLCJpc3MiOiJodHRwczovL2xvZ2luLm1pY3Jvc29mdG9ubGluZS5jb20vODhkYjUzZGQtODRmNC00NDMxLWE2ZTctNTQ1M2Y2MDdiODlkL3YyLjAiLCJpYXQiOjE3MTg5NTI2MjMsIm5iZiI6MTcxODk1MjYyMywiZXhwIjoxNzE4OTU2NTIzLCJlbWFpbCI6ImkyMGl3YWlAbWl5YXpha2ktbGFiLm9yZyIsImlkcCI6Imh0dHBzOi8vc3RzLndpbmRvd3MubmV0LzkxODgwNDBkLTZjNjctNGM1Yi1iMTEyLTM2YTMwNGI2NmRhZC8iLCJuYW1lIjoi5bKp5LqVIOe_lOS4gCIsIm9pZCI6IjJhN2YzMDM4LTI5ZmUtNDMwOC04MjVmLWQ2MjE4ODRjZmEzMyIsInByZWZlcnJlZF91c2VybmFtZSI6ImkyMGl3YWlAbWl5YXpha2ktbGFiLm9yZyIsInJoIjoiMC5BV3NBM1ZQYmlQU0VNVVNtNTFSVDlnZTRuVXBpMWZvRS1TTkxoMWdHS3d4Uk5tRnJBSm8uIiwic3ViIjoiNlhwZW1NWXNLd19RY3ZZNnQ4aGxFX2dWOWNXMERGTHJTMnhPRlhlVGJmRSIsInRpZCI6Ijg4ZGI1M2RkLTg0ZjQtNDQzMS1hNmU3LTU0NTNmNjA3Yjg5ZCIsInV0aSI6IlJ2bXRQbHpGZ1UtSXFpSDhtdzRuQUEiLCJ2ZXIiOiIyLjAifQ.TTBE538JO7RZKBKjQPEoL4uk5uPY-Sv2Opy4efAs9eU"
    return jwt.decode(encoded_jwt, SECRET_KEY, algorithms=[ALGORITHM])


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
