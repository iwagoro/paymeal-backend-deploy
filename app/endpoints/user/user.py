from fastapi import HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import or_
from util.util import get_db, verify_token, create_response, create_error_response
from models import Users, AdminUsers, Orders
from fastapi.responses import JSONResponse, Response
from sqlalchemy.sql import extract
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import os
import pytz


router = APIRouter()


# * ユーザを確認する関数
def get_user_by_email(db: Session, email: str):
    user = db.query(Users).filter_by(email=email).first()
    if not user:
        raise HTTPException(status_code=401, detail="UNAUTHORIZED")
    return user


#! email/idを取得
@router.get("/user")
async def get_user(user=Depends(verify_token), db: Session = Depends(get_db)):
    # ? ユーザを取得
    target = get_user_by_email(db, user["email"])
    # ? レスポンスの作成
    return {"user": target}


#! 追加
@router.post("/user")
async def add_user(user=Depends(verify_token), db: Session = Depends(get_db)):
    try:
        # ? レスポンスの作成
        new_user = Users(id=user["uid"], email=user["email"])
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return Response(status_code=201)
    # ? 競合エラー
    except IntegrityError:
        raise HTTPException(status_code=400, detail="User already exists")
    # ? その他のエラー
    except SQLAlchemyError:
        raise HTTPException(status_code=400, detail="Invalid Request")


#! ユーザの今月の購入額を取得
@router.get("/user/usage", status_code=200)
async def get_user_monthly_usage(user=Depends(verify_token), db: Session = Depends(get_db)):
    # ? ユーザを取得
    target = get_user_by_email(db, user["email"])
    tokyo_tz = pytz.timezone("Asia/Tokyo")
    # ? ユーザの今月の注文を取得
    result = (
        db.query(Orders)
        .filter(
            Orders.user_id == target.id,
            or_(Orders.status == "purchased", Orders.status == "ordered", Orders.status == "completed"),
            extract("month", Orders.date) == datetime.now(tokyo_tz).month,
        )
        .all()
    )
    if not result:
        raise HTTPException(status_code=404, detail="No orders found")
    total = sum([item.total for item in result])
    return {"total": total}


#! ユーザの先月の購入額を取得
@router.get("/user/usage/last_month", status_code=200)
async def get_user_last_monthly_usage(user=Depends(verify_token), db: Session = Depends(get_db)):
    # ? ユーザを取得
    target = get_user_by_email(db, user["email"])
    tokyo_tz = pytz.timezone("Asia/Tokyo")
    # ? ユーザの先月の注文を取得
    result = (
        db.query(Orders)
        .filter(
            Orders.user_id == target.id,
            or_(Orders.status == "purchased", Orders.status == "ordered", Orders.status == "completed"),
            extract("month", Orders.date) == datetime.now(tokyo_tz).month - 1,
        )
        .all()
    )
    if not result:
        raise HTTPException(status_code=404, detail="No orders found")
    total = sum([item.total for item in result])
    return {"total": total}
