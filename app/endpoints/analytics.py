from fastapi import HTTPException, Depends, Response, APIRouter, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from models import Users, Orders, OrderItems, Tickets, AdminUsers
from util.util import get_db, verify_token, create_response, create_error_response
from datetime import datetime, timedelta
from typing import Optional, List

router = APIRouter()


# * ユーザを確認する関数
def get_user_by_email(db: Session, email: str):
    user = db.query(AdminUsers).filter_by(email=email).first()
    if not user:
        raise HTTPException(status_code=401, detail="UNAUTHORIZED")
    return user


#! １ヶ月間の各日の売上を取得
@router.get("/analytics/sales/monthly")
def get_monthly_sales(user=Depends(verify_token), db: Session = Depends(get_db)):

    # ?管理者の確認
    target = db.query(AdminUsers).filter_by(email=user["email"]).first()

    # ?今日の日付を取得
    today = datetime.now()
    year = today.year
    month = today.month
    # ?月初と月末を取得
    start = datetime(year, month, 1)
    end = datetime(year, month + 1, 1)
    # ?1ヶ月月の注文を取得
    orders = (
        db.query(Orders)
        .filter(
            or_(Orders.status == "purchased", Orders.status == "ordered", Orders.status == "completed"),
            Orders.date >= start,
            Orders.date < end,
        )
        .all()
    )
    # ?売上を計算
    sales = []
    for i in range(1, (end - timedelta(days=1)).day):
        day = datetime(year, month, i)
        daily_total = sum([order.total for order in orders if order.date == day])
        sales.append({"date": day, "total": daily_total})

    return {"sales": sales}


#! 今日の売上を取得
@router.get("/sales/daily", status_code=200)
async def get_daily_sales(user=Depends(verify_token), db: Session = Depends(get_db)):
    # ?管理者の確認
    target = db.query(AdminUsers).filter_by(email=user["email"]).first()
    # ?今日の日付を取得
    today = datetime.now().date()

    # ?今日の売上を取得
    result = db.query(Orders).filter(Orders.date == today).all()
    if not result:
        raise HTTPException(status_code=404, detail="NO SALES FOUND")

    return {"total": sum([order.total for order in result])}


#! 今週の売上を取得
@router.get("/sales/weekly", status_code=200)
async def get_weekly_sales(user=Depends(verify_token), db: Session = Depends(get_db)):
    # ? 管理者の確認
    target = db.query(AdminUsers).filter_by(email=user["email"]).first()

    # ? 今日の日付を取得
    today = datetime.today().date()
    start = today - timedelta(days=today.weekday())
    end = start + timedelta(days=6)

    # ?今週の注文を取得
    result = db.query(Orders).filter(Orders.date >= start, Orders.date <= end).all()
    if not result:
        raise HTTPException(status_code=404, detail="NO SALES FOUND")

    return {"total": sum([order.total for order in result])}


#! 今月の売上を取得
@router.get("/sales/monthly", status_code=200)
async def get_monthly_sales(user=Depends(verify_token), db: Session = Depends(get_db)):
    # ? 管理者の確認
    target = db.query(AdminUsers).filter_by(email=user["email"]).first()
    # ? 今日の日付を取得
    today = datetime.today().date()
    start = today.replace(day=1)
    end = today.replace(day=1, month=today.month + 1) - timedelta(days=1)

    # ? 今月の注文を取得
    result = db.query(Orders).filter(Orders.date >= start, Orders.date <= end).all()
    if not result:
        raise HTTPException(status_code=404, detail="NO SALES FOUND")

    return {"total": sum([order.total for order in result])}
